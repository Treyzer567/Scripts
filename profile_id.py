import os
import requests
import sys

# --- Configuration ---
# Set these via environment variables or edit directly for local use
SONARR_URL = os.getenv("SONARR_URL", "http://your-server-ip:8989")
SONARR_API_KEY = os.getenv("SONARR_API_KEY", "")

def get_profiles():
    if not SONARR_API_KEY:
        print("Error: SONARR_API_KEY environment variable is missing.")
        return

    endpoint = f"{SONARR_URL}/api/v3/qualityprofile"
    headers = {'X-Api-Key': SONARR_API_KEY}

    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        profiles = response.json()

        print(f"\n{'ID':<5} | {'Name'}")
        print("-" * 25)
        for profile in profiles:
            print(f"{profile['id']:<5} | {profile['name']}")
        print("-" * 25)
        print("Use the 'ID' number in your sonarr_map.json file.\n")

    except requests.exceptions.RequestException as e:
        print(f"Failed to connect to Sonarr: {e}")

if __name__ == "__main__":
    get_profiles()
