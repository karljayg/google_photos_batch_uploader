import csv
import re

# Path to the log file
log_file_path = 'upload_log.txt'

# Path to the new CSV file where details of successfully processed files will be saved
csv_file_path = 'processed_files_details.csv'

def process_log_file(log_file_path, csv_file_path):
    with open(log_file_path, 'r') as log_file:
        lines = log_file.readlines()

    # Prepare the data to be written to the CSV file
    rows = []
    for line in lines:
        # Filtering lines which represent successful uploads
        if re.search(r'\bHash\b', line) and not re.search(r'\bError uploading\b', line):
            details = line.strip().split(', ')
            row = {
                'Datetime': details[0],
                'File Path': details[1],
                'Size (bytes)': details[2],
                'Hash': details[3].split(' ')[1],
                'Creation Time': details[4],
                'Modification Time': details[5],
                'Access Time': details[6],
                'Elapsed Time': details[7],
                'File Number': details[8],
                'Total Files': details[9]
            }
            rows.append(row)

    # Write the data to the new CSV file
    with open(csv_file_path, 'w', newline='') as csvfile:
        fieldnames = ['Datetime', 'File Path', 'Size (bytes)', 'Hash', 'Creation Time', 'Modification Time', 'Access Time', 'Elapsed Time', 'File Number', 'Total Files']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(rows)

    print(f"Successfully processed the log file. Details of {len(rows)} files have been saved to {csv_file_path}.")

# Execute the function
process_log_file(log_file_path, csv_file_path)

