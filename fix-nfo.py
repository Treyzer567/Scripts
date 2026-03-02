import os
import re
import xml.etree.ElementTree as ET

# Set this to your actual One Pace folder path
base_path = "/mnt/Anime/Anime/One Pace"

def fix_nfo_files(directory):
    # Regex to find "One Pace - SxxExx - " at the start of a title
    pattern = re.compile(r'^One Pace\s*-\s*S\d+E\d+\s*-\s*', re.IGNORECASE)

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".nfo"):
                file_path = os.path.join(root, file)
                
                try:
                    tree = ET.parse(file_path)
                    root_node = tree.getroot()
                    
                    title_node = root_node.find('title')
                    if title_node is not None and title_node.text:
                        # Remove the "One Pace - SXXEXX - " part
                        new_title = pattern.sub('', title_node.text)
                        
                        if new_title != title_node.text:
                            print(f"Fixing Title: {title_node.text} -> {new_title}")
                            title_node.text = new_title
                    
                    # Force lockdata to true so Jellyfin stops overwriting
                    lock_node = root_node.find('lockdata')
                    if lock_node is not None:
                        lock_node.text = 'true'
                    else:
                        new_lock = ET.SubElement(root_node, 'lockdata')
                        new_lock.text = 'true'

                    # Save the cleaned NFO
                    tree.write(file_path, encoding='utf-8', xml_declaration=True)
                    
                except Exception as e:
                    print(f"Error processing {file}: {e}")

if __name__ == "__main__":
    fix_nfo_files(base_path)
