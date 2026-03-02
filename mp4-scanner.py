import os
from pathlib import Path

def main():
    # 1. Ask the user for the directory to scan
    dir_input = input("Enter the directory path to scan (press Enter for the current directory): ").strip()
    
    if not dir_input:
        scan_dir = Path.cwd()
    else:
        scan_dir = Path(dir_input)
        
    # Verify the directory exists
    if not scan_dir.exists() or not scan_dir.is_dir():
        print(f"Error: The directory '{scan_dir}' does not exist or is not a valid directory.")
        return

    print(f"\nScanning '{scan_dir}' for .mp4 files...")
    
    # 2. Find all .mp4 files (rglob makes it recursive, searching subfolders too)
    mp4_files = list(scan_dir.rglob("*.mp4"))
    
    # 3. Check if any files were found
    if not mp4_files:
        print("No .mp4 files found in this directory.")
        return
        
    # 4. List the files
    print(f"\nFound {len(mp4_files)} .mp4 file(s):")
    for file_path in mp4_files:
        print(f" - {file_path}")
        
    # 5. Ask for confirmation to delete
    print("\n⚠️ WARNING: This will permanently delete these files. They will not go to the Recycle Bin/Trash.")
    confirm = input("Would you like to delete ALL of these files? (y/n): ").strip().lower()
    
    # 6. Delete or exit based on user input
    if confirm in ['y', 'yes']:
        print("\nDeleting files...")
        deleted_count = 0
        for file_path in mp4_files:
            try:
                file_path.unlink() # This is the command that deletes the file
                print(f"Deleted: {file_path.name}")
                deleted_count += 1
            except Exception as e:
                print(f"Failed to delete {file_path.name}: {e}")
                
        print(f"\nSuccessfully deleted {deleted_count} file(s).")
    else:
        print("\nDeletion cancelled. No files were harmed. Exiting...")

if __name__ == "__main__":
    main()
