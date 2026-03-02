# Scripts

A collection of utility scripts for managing a self-hosted media server. Includes automated media movers, Sonarr/Jellyfin helpers, and one-off maintenance tools. Most scripts are designed to run as scheduled Docker containers, while others are standalone utilities run manually.

---

## Media Mover Scripts

These scripts watch a source directory and move files into the correct destination folder based on Sonarr metadata or a manual mapping file. They are intended to run on a schedule (e.g. hourly) inside Docker containers via `scripts-compose.yml`.

| Script | Description |
|--------|-------------|
| `show-mover.py` | Moves TV shows and anime into categorized destination folders using Sonarr tags (`anime`, `tv`, `kids`) and `show_map.json` |
| `movie-mover.py` | Moves movies into the correct destination folder |
| `music-mover.py` | Moves music files into the music library |
| `comic-mover.py` | Moves comic files into the comics library |
| `manga-mover.py` | Moves manga files into the manga library |
| `novel-mover.py` | Moves ebook/novel files into the novels library |
| `webcomic-mover.py` | Moves webcomic files into the webcomics library |
| `musicals-mover.py` | Moves musical content into the musicals library |
| `youtube-mover.py` | Moves downloaded YouTube content into the YouTube library |

### Mapping Files

| File | Description |
|------|-------------|
| `show_map.json` | Manual overrides for show → destination category mapping |
| `sonarr_map.json` | Maps Sonarr series IDs to quality profile names |

---

## Sonarr / Automation Helpers

| Script | Description |
|--------|-------------|
| `anime_profile_updater.py` | Automatically updates Sonarr quality profiles for anime series based on `sonarr_map.json`. Runs on a schedule via Docker. Requires `SONARR_URL` and `SONARR_API_KEY` env vars. May require the use of `profile_id.py` to find the profile IDs. |
| `profile_id.py` | One-off utility to list all Sonarr quality profile IDs and names — useful for building `sonarr_map.json` |

---

## Maintenance / One-Off Tools

These scripts are run manually rather than on a schedule.

| Script | Description |
|--------|-------------|
| `organize_movies.py` | Organizes loose movie files into properly named subfolders. Need to manually set variables in the file. |
| `fix-nfo.py` | Fixes malformed `.nfo` metadata files for One Pace episodes |
| `mp4-scanner.py` | Scans a directory and lists all `.mp4` files — useful for finding unconverted media. Uses current directory or a set one. |
| `onepace.sh` | Renames One Pace video files to a standard `SxxExx` format in bulk |
| `volume-maker.sh` | Bundles individual manga chapter `.cbz` files into volume archives |

---

## Deployment

Scheduled scripts run as Docker containers defined in `scripts-compose.yml`. Each mover runs in a loop with a 1-hour sleep between executions.

### Environment Variables

| Variable | Description | Used By |
|----------|-------------|---------|
| `SONARR_URL` | Internal URL of your Sonarr instance | `show-mover.py`, `anime_profile_updater.py` |
| `SONARR_API_KEY` | Sonarr API key | `show-mover.py`, `anime_profile_updater.py` |

### Volume Mounts

Each mover script requires source and destination paths mounted into the container. Update the volume paths in `scripts-compose.yml` to match your server's directory layout before deploying.

---

## Related Repos

| Repo | Description |
|------|-------------|
| [landing-page](https://github.com/Treyzer567/landing-page) | Frontend hub — includes a Script Runner UI for triggering movers manually |
| [script-runner](https://github.com/Treyzer567/script-runner) | Backend API that the Script Runner UI talks to |
| [manga-renamer](https://github.com/Treyzer567/manga-renamer) | Manga/Webtoons renaming script |

---

## External Projects

| Project | Description |
|---------|-------------|
| [Sonarr](https://github.com/Sonarr/Sonarr) | TV series collection manager — used for show categorization and quality profiles |
| [Jellyfin](https://github.com/jellyfin/jellyfin) | Open source media server — destination for moved media |
| [Booklore](https://github.com/booklore-app/booklore) | Self-hosted book server - destination for manga, webcomic and novels |

