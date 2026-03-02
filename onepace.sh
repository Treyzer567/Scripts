#!/bin/bash

# Loop through all video files in the current directory
for video in *.{mkv,mp4,avi}; do
    # Skip if file doesn't exist (handles empty folder cases)
    [ -e "$video" ] || continue

    # Extract the S0XE0X part (e.g., S01E05)
    if [[ $video =~ (S[0-9]{2}E[0-9]{2}) ]]; then
        ep_code="${BASH_REMATCH[1]}"
        
        # Find the .nfo file that contains the same code
        nfo_file=$(ls | grep "$ep_code" | grep "\.nfo$" | head -n 1)

        if [ -n "$nfo_file" ]; then
            # Get the base name of the NFO (everything before .nfo)
            new_name="${nfo_file%.nfo}"
            extension="${video##*.}"
            
            echo "Matching: $video  -->  $new_name.$extension"
            
            # Uncomment the next line once you've verified the output
            # mv "$video" "$new_name.$extension"
        else
            echo "No matching NFO found for $video"
        fi
    fi
done
