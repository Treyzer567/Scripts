import os
import json
import time
import logging
import requests
import sys

# --- Configuration ---
SONARR_URL = os.environ.get('SONARR_URL', 'http://sonarr:8989').rstrip('/')
SONARR_API_KEY = os.environ.get('SONARR_API_KEY')
MAP_FILE = '/scripts/sonarr_map.json'
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()

# --- Logging Setup ---
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=LOG_LEVEL,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def get_headers():
    return {'X-Api-Key': SONARR_API_KEY, 'Content-Type': 'application/json'}

def load_map():
    """Explicitly re-reads the JSON file from disk on every call."""
    logger.info(f"Syncing configuration from {MAP_FILE}...")
    if not os.path.exists(MAP_FILE):
        logger.error(f"Map file not found at {MAP_FILE}")
        return []
    try:
        with open(MAP_FILE, 'r') as f:
            data = json.load(f)
            # Count enabled shows for logging
            enabled_count = sum(1 for show in data if show.get('enabled', True))
            logger.info(f"Loaded {len(data)} total entries ({enabled_count} enabled).")
            return data
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON map. Check your syntax!")
        return []

def save_map(data):
    try:
        with open(MAP_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        logger.info("Saved updated state to sonarr_map.json.")
    except Exception as e:
        logger.error(f"Failed to save map file: {e}")

def get_series_id(title):
    try:
        url = f"{SONARR_URL}/api/v3/series"
        resp = requests.get(url, headers=get_headers())
        resp.raise_for_status()
        all_series = resp.json()
        
        for show in all_series:
            if show['title'].lower() == title.lower():
                return show['id']
                
        logger.warning(f"Series '{title}' not found in Sonarr library.")
        return None
    except Exception as e:
        logger.error(f"Error looking up series {title}: {e}")
        return None

def get_episodes(series_id):
    url = f"{SONARR_URL}/api/v3/episode?seriesId={series_id}"
    resp = requests.get(url, headers=get_headers())
    resp.raise_for_status()
    return resp.json()

def swap_profile(series_id, profile_id):
    get_url = f"{SONARR_URL}/api/v3/series/{series_id}"
    series_resp = requests.get(get_url, headers=get_headers())
    series_data = series_resp.json()

    series_data['qualityProfileId'] = profile_id
    
    put_url = f"{SONARR_URL}/api/v3/series/{series_id}"
    requests.put(put_url, json=series_data, headers=get_headers())
    logger.info(f"Swapped Series ID {series_id} to Profile ID {profile_id}")

def remonitor_episodes(episode_ids):
    """
    Directly updates the monitoring status using the PUT /episode/monitor endpoint.
    This is more reliable than the general 'Command' endpoint for bulk changes.
    """
    if not episode_ids:
        return
    
    payload = {
        "episodeIds": episode_ids,
        "monitored": True
    }
    # Sonarr v3/v4 uses this specific bulk endpoint
    url = f"{SONARR_URL}/api/v3/episode/monitor"
    resp = requests.put(url, json=payload, headers=get_headers())
    
    if resp.status_code in [200, 202]:
        logger.info(f"Successfully set 'monitored' to True for {len(episode_ids)} episodes.")
    else:
        logger.error(f"Failed to update monitoring. Status: {resp.status_code}, Body: {resp.text}")

def process_shows():
    # Fresh load at the start of every run
    shows_map = load_map()
    shows_modified = False

    if not shows_map:
        return

    for show_entry in shows_map:
        if not show_entry.get('enabled', True):
            continue

        title = show_entry['title']
        target_profile = show_entry['target_profile_id']
        
        series_id = get_series_id(title)
        if not series_id:
            continue

        episodes = get_episodes(series_id)
        if not episodes:
            continue

        # Find latest season (ignoring specials/season 0)
        seasons = [ep.get('seasonNumber', 0) for ep in episodes if ep.get('seasonNumber') != 0]
        if not seasons:
            continue

        max_season = max(seasons)
        season_eps = [ep for ep in episodes if ep.get('seasonNumber') == max_season]
        season_eps.sort(key=lambda x: x['episodeNumber'])
        last_ep = season_eps[-1]

        # Trigger: If the finale is unmonitored
        if last_ep['monitored'] is False:
            logger.info(f"Finale for '{title}' (S{max_season}E{last_ep['episodeNumber']}) is unmonitored. Updating...")
            
            # 1. Swap Profile
            swap_profile(series_id, target_profile)
            
            # 2. Remonitor the whole season
            ep_ids_to_monitor = [ep['id'] for ep in season_eps]
            remonitor_episodes(ep_ids_to_monitor)
            
            # 3. Disable this show in the map
            show_entry['enabled'] = False
            shows_modified = True
        else:
            logger.debug(f"'{title}' finale is still monitored. Skipping.")

    if shows_modified:
        save_map(shows_map)
    else:
        logger.info("No changes required this cycle.")

if __name__ == "__main__":
    if not SONARR_API_KEY:
        logger.error("SONARR_API_KEY environment variable is missing!")
        sys.exit(1)
        
    process_shows()
