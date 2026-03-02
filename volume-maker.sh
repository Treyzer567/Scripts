#!/usr/bin/env bash

CHAPS_PER_VOL=20
OUTPUT_DIR="complete"
TMP_ROOT="_tmp_volume"

mkdir -p "$OUTPUT_DIR"

# Load chapters safely
mapfile -d '' chapters < <(find . -maxdepth 1 -type f -name "* - Chapter *.cbz" -print0 | sort -zV)

total=${#chapters[@]}
if [[ $total -eq 0 ]]; then
    echo "No chapter files found!"
    exit 1
fi

# Determine title from first file
first="${chapters[0]}"
first="${first#./}"
title=$(echo "$first" | sed -E 's/ - Chapter .+//')

echo "Series detected: $title"
echo "Chapters found: $total"

vol=1
index=0

while [[ $index -lt $total ]]; do
    vol_name=$(printf "%s - v%03d.cbz" "$title" "$vol")
    THIS_TMP="$TMP_ROOT-$vol"

    rm -rf "$THIS_TMP"
    mkdir -p "$THIS_TMP"

    # Process 20 chapters
    count=0
    while [[ $count -lt $CHAPS_PER_VOL && $index -lt $total ]]; do

        chap_file="${chapters[$index]}"
        chap_file="${chap_file#./}"

        # Extract chapter number
        chap_num=$(echo "$chap_file" | sed -E 's/.* - Chapter ([0-9]+)\.cbz/\1/')

        echo "Adding Chapter $chap_num to volume $vol..."

        # Temporary extraction folder
        chap_tmp="$THIS_TMP/chap_$chap_num"
        mkdir -p "$chap_tmp"

        # Extract the CBZ (zip)
        unzip -qq "$chap_file" -d "$chap_tmp"

        # Rename extracted image files
        pagenum=1
        shopt -s nullglob
        for img in "$chap_tmp"/*.{jpg,jpeg,png,webp,JPG,JPEG,PNG,WEBP}; do
            # Rename extracted image files
	   chap_num_decimal=$((10#$chap_num))
	   newname=$(printf "%s - Chapter %03d - Page %03d.%s" \
            		"$title" "$chap_num_decimal" "$pagenum" "${img##*.}")

            mv "$img" "$THIS_TMP/$newname"
            ((pagenum++))
        done
        shopt -u nullglob

        rm -rf "$chap_tmp"
        ((index++))
        ((count++))
    done

    # Build ComicInfo.xml
    cat > "$THIS_TMP/ComicInfo.xml" <<EOF
<?xml version="1.0"?>
<ComicInfo>
  <Series>$title</Series>
  <Volume>$vol</Volume>
  <Summary>Auto-generated combined volume $vol.</Summary>
  <Language>en</Language>
</ComicInfo>
EOF

    echo "Creating volume archive: $vol_name"
    (cd "$THIS_TMP" && zip -r "../$OUTPUT_DIR/$vol_name" . > /dev/null)

    rm -rf "$THIS_TMP"
    ((vol++))
done

echo "All volumes created in ./$OUTPUT_DIR/"

