import pandas as pd
import os
import shutil


# Function to move files to a specified folder
def move_to_delete_folder(file_path, delete_folder):
    try:
        # Create the DELETE folder if it doesn't exist
        os.makedirs(delete_folder, exist_ok=True)

        # Generate the new file path in the DELETE folder
        new_file_path = os.path.join(delete_folder, os.path.basename(file_path))

        # Move the file to the DELETE folder
        shutil.move(file_path, new_file_path)

        return True
    except Exception as e:
        print(f"Error moving file: {file_path}, Error: {str(e)}")
        return False


# Function to safely move duplicate files to the DELETE folder
# Function to safely move duplicate files to the DELETE folder
def move_duplicates(input_csv, delete_folder):
    # Load the full CSV into a DataFrame
    df = pd.read_csv(input_csv)

    # Initialize variables to keep track of progress
    total_moved_files = 0
    total_moved_size = 0

    # Group the DataFrame by the "MD5 Hash" column
    duplicate_groups = df[df.duplicated(subset=['MD5 Hash'], keep=False)]

    for md5_hash, group in duplicate_groups.groupby(['MD5 Hash']):
        print(f"MD5 Hash: {md5_hash}")
        print(f"Total duplicates in this group: {len(group)}")

        # Sort the group by size in descending order
        group = group.sort_values(by=['Size'], ascending=False)

        # Keep the first row (largest file) and move the rest to the DELETE folder
        keep_row = group.iloc[0]
        move_rows = group.iloc[1:]

        for _, move_row in move_rows.iterrows():
            try:
                # Get the file path for the row to move
                file_path = move_row['Clickable Link'].split('"')[1]  # Extract the file path from the hyperlink

                # Move the file to the DELETE folder
                if os.path.exists(file_path):
                    moved = move_to_delete_folder(file_path, delete_folder)
                    if moved:
                        total_moved_files += 1
                        total_moved_size += move_row['Size']
                        print(f"Moved to DELETE: {file_path}, Size: {move_row['Size']} bytes")
                    else:
                        print(f"Error moving file: {file_path}")
                else:
                    print(f"File not found: {file_path}")
            except Exception as e:
                print(f"Error moving file: {file_path}, Error: {str(e)}")

    print(f"Total moved files: {total_moved_files}")
    print(f"Total moved size: {total_moved_size} bytes")


if __name__ == "__main__":
    input_csv = "file_inventory.csv"  # Replace with your full input CSV file
    delete_folder = r"C:\Users\karl_\Downloads\JMU_DUPES"  # Specify the folder where duplicate files will be moved

    move_duplicates(input_csv, delete_folder)
