import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

MOOD_QUERIES = {
    "happy": "happy upbeat songs playlist",
    "sad": "sad emotional songs playlist",
    "angry": "calm meditation music",
    "fear": "brave motivational songs playlist",
    "calm": "relaxing instrumental music",
    "neutral": "lofi chill music"
}

import json
import random

MOOD_DB_PATH = os.path.join(os.path.dirname(__file__), 'mood_music.json')


def load_local_db():
    try:
        with open(MOOD_DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print('Could not load local mood DB:', e)
        return {}


def _parse_iso8601_duration(dur_str):
    # Simple ISO 8601 duration parser for hours/minutes/seconds (PT#H#M#S)
    try:
        import re
        m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', dur_str)
        if not m:
            return None
        h = int(m.group(1) or 0)
        mm = int(m.group(2) or 0)
        s = int(m.group(3) or 0)
        if h:
            return f"{h}:{mm:02d}:{s:02d}"
        return f"{mm}:{s:02d}"
    except Exception:
        return None


def get_music_list(mood, limit=5):
    mood_key = (mood or 'neutral').lower()

    query = MOOD_QUERIES.get(mood_key, 'chill music')

    # 0) Prefer YouTube when API key is available
    results = []
    if API_KEY:
        try:
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "q": query,
                "key": API_KEY,
                "maxResults": limit,
                "type": "video",
                "videoCategoryId": "10"
            }
            resp = requests.get(url, params=params, timeout=8)
            resp.raise_for_status()
            res = resp.json()

            ids = []
            items_map = {}
            for item in res.get('items', []):
                vid = item.get('id', {}).get('videoId')
                snippet = item.get('snippet', {})
                title = snippet.get('title')
                channel = snippet.get('channelTitle')
                if vid:
                    ids.append(vid)
                    items_map[vid] = {'name': title or f'Video {vid}', 'url': f'https://www.youtube.com/watch?v={vid}', 'channel': channel}

            # If we have ids, fetch contentDetails for durations
            if ids:
                try:
                    vids = ','.join(ids)
                    vurl = "https://www.googleapis.com/youtube/v3/videos"
                    vparams = {"part": "contentDetails,snippet", "id": vids, "key": API_KEY}
                    vresp = requests.get(vurl, params=vparams, timeout=8)
                    vresp.raise_for_status()
                    vres = vresp.json()
                    for v in vres.get('items', []):
                        vid = v.get('id')
                        cd = v.get('contentDetails', {})
                        duration = cd.get('duration')
                        # parse ISO 8601 duration like PT3M45S
                        parsed = None
                        if duration:
                            parsed = _parse_iso8601_duration(duration)
                        # update map
                        if vid in items_map:
                            items_map[vid]['duration'] = parsed
                            items_map[vid]['channel'] = v.get('snippet', {}).get('channelTitle') or items_map[vid].get('channel')

                except Exception as e:
                    print('Music API error fetching video details (durations):', e)

            # Build results list preserving order
            for vid in ids:
                entry = items_map.get(vid)
                if entry:
                    results.append(entry)

            if results:
                return results
        except Exception as e:
            print('Music API error when fetching list:', e)

    # 1) Try DB (Mongo) next
    try:
        from backend.database import db as _db
        if _db:
            coll = _db['mood_music']
            doc = coll.find_one({'mood': mood_key})
            if doc and 'tracks' in doc:
                return doc['tracks'][:limit]
    except Exception:
        # ignore DB errors and fallback to local file
        pass

    # 2) Local JSON file
    local = load_local_db()
    if local:
        # Prefer exact mood list first, then Hindi-specific variants
        combined = []
        hindi_key = f"hindi_{mood_key}"
        if mood_key in local:
            combined.extend(local[mood_key])
        if hindi_key in local:
            combined.extend(local[hindi_key])

        if combined:
            tracks = combined[:limit]
            # ensure consistent shape (name,url)
            return [{'name': t.get('name'), 'url': t.get('url')} if isinstance(t, dict) else {'name': str(t), 'url': t} for t in tracks]

    # Final fallback is a search page
    return [{'name': query, 'url': f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"}]


def get_music_link(mood):
    # convenience: return first available link
    lst = get_music_list(mood, limit=1)
    if lst:
        return lst[0]['url']
    return None
