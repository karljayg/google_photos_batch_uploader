import os
import hashlib
import pandas as pd
import time
from datetime import datetime


# Function to calculate MD5 hash of a file
def calculate_md5(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as file:
        while True:
            data = file.read(65536)  # Read in 64k chunks
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()


# Function to generate file inventory and identify duplicates
def generate_file_inventory(start_folder, output_csv):
    file_info_list = []
    total_files_processed = 0
    md5_dict = {}  # Dictionary to store MD5 hashes and their corresponding file paths

    # Start the timer
    start_time = time.time()

    # Walk through the folders and collect file information
    for root, _, files in os.walk(start_folder):
        for filename in files:
            total_files_processed += 1
            file_path = os.path.join(root, filename)
            file_size = os.path.getsize(file_path)
            modified_time = os.path.getmtime(file_path)
            created_time = os.path.getctime(file_path)
            md5_hash = calculate_md5(file_path)

            # Replace backslashes with forward slashes in the file path
            file_path = file_path.replace("\\", "/")

            # Create a clickable link to the file using =HYPERLINK formula
            clickable_link = f'=HYPERLINK("{file_path}", "Open File")'

            # Create a clickable link to open the folder in Windows Explorer
            folder_link = f'=HYPERLINK("{os.path.dirname(file_path)}","Open Folder")'

            # Check for duplicates
            if md5_hash in md5_dict:
                likely_duplicate = "Yes"
                duplicate_file_path = md5_dict[md5_hash]
                duplicate_file_link = f'=HYPERLINK("{duplicate_file_path}", "Open File")'
                duplicate_folder_link = f'=HYPERLINK("{os.path.dirname(duplicate_file_path)}", "Open Folder")'
            else:
                likely_duplicate = "No"
                duplicate_file_link = ""
                duplicate_folder_link = ""
                md5_dict[md5_hash] = file_path

            file_info = {
                'Path': os.path.relpath(root, start_folder),
                'Filename': filename,
                'Size': file_size,
                'Modified Time': datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d %H:%M:%S'),
                'Created Time': datetime.fromtimestamp(created_time).strftime('%Y-%m-%d %H:%M:%S'),
                'MD5 Hash': md5_hash,
                'Clickable Link': clickable_link,
                'Folder Link': folder_link,
                'Likely Duplicate': likely_duplicate,  # Add likely duplicate status here
                'Duplicate File Link': duplicate_file_link,  # Add link to duplicate file
                'Duplicate Folder Link': duplicate_folder_link,  # Add link to duplicate folder
            }

            file_info_list.append(file_info)

            # Print vital stats
            elapsed_time = time.time() - start_time
            print(
                f"Processed {total_files_processed} files out of {total_files_count}, Elapsed Time: {elapsed_time:.2f} seconds")
            print(f"Path: {os.path.relpath(root, start_folder)}, Filename: {filename}, Size: {file_size} bytes")

    # Create a DataFrame from the collected file information
    inventory_df = pd.DataFrame(file_info_list)

    # Save the DataFrame to a CSV file
    inventory_df.to_csv(output_csv, index=False)


if __name__ == "__main__":
    # start_folder = r"D:\RECOVERY\MyBook_backups\KJ_LAPTOP_T60\NeuStar T60 (C)\kgarcia\VISTALAPTOP\Users\Karl\Documents\PICS_VIDEOS"
    start_folder = r"C:\Users\karl_\Downloads\JMU"
    output_csv = "file_inventory.csv"

    # Count the total number of files
    total_files_count = sum(len(files) for _, _, files in os.walk(start_folder))

    # Generate the file inventory
    generate_file_inventory(start_folder, output_csv)
