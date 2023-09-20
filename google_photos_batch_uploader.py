from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import requests
import os
import time
import hashlib
from datetime import datetime
import csv

# Initialize the log file
log_file_path = 'upload_log.txt'
temp_log_file_path = 'temp_upload_log.txt'
log_file = open(temp_log_file_path, 'a')
# Define a variable to hold the folder path
folder_path_to_upload = r'D:\RECOVERY\PICS_VIDEOS\STUFF\upload'


def log_and_print(message):
    print(message)
    log_file.write(message + '\n')


# Create a set to hold hashes of already uploaded files
uploaded_file_hashes = set()
if os.path.exists('processed_files_details.csv'):
    with open('processed_files_details.csv', 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader)  # Skip the header row
        for row in csv_reader:
            uploaded_file_hashes.add(row[3])  # Updated to read hash from the correct column
else:
    with open(log_file_path, 'r') as f:
        for line in f:
            try:
                uploaded_file_hashes.add(line.split('Hash: ')[1].split(',')[0])
            except IndexError:
                continue

# Initialize the OAuth2 flow
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.appendonly']
creds = None

if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('settings/token.json', SCOPES)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'settings/KJ_personal_credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('settings/token.json', 'w') as token:
        token.write(creds.to_json())

# Build the service
service = build('photoslibrary', 'v1', credentials=creds)


def upload_photo(file_path, file_number, total_files):
    start_time = datetime.now()
    try:
        with open(file_path, 'rb') as f:
            file_data = f.read()
            file_hash = hashlib.md5(file_data).hexdigest()

        file_name_without_extension = os.path.splitext(os.path.basename(file_path))[0]
        path_parts = os.path.normpath(file_path).split(os.sep)
        last_two_folders = os.path.join(path_parts[-3], path_parts[-2]) if len(path_parts) > 2 else path_parts[-2]
        description = f"Path: {last_two_folders}/{os.path.basename(file_path)}, Description for {file_name_without_extension}, Hash: {file_hash}"

        # Skip file if it has already been uploaded
        if file_hash in uploaded_file_hashes:
            log_and_print(f"Skipping already uploaded file: {os.path.basename(file_path)} ({file_number}/{total_files})")
            return

        # Skip thumbnails
        if "thmb" in file_name_without_extension or "thumb" in file_name_without_extension:
            log_and_print(f"Skipping thumbnail: {os.path.basename(file_path)} ({file_number}/{total_files})")
            return

        upload_url = "https://photoslibrary.googleapis.com/v1/uploads"
        headers = {
            "Authorization": f"Bearer {creds.token}",
            "Content-type": "application/octet-stream",
            "X-Goog-Upload-File-Name": os.path.basename(file_path),
            "X-Goog-Upload-Protocol": "raw"
        }

        with open(file_path, 'rb') as photo:
            response = requests.post(upload_url, headers=headers, data=photo)
            upload_token = response.content.decode('utf-8')

        create_media_item_request = {
            "newMediaItems": [
                {
                    "description": description,
                    "simpleMediaItem": {
                        "uploadToken": upload_token
                    }
                }
            ]
        }

        response = service.mediaItems().batchCreate(body=create_media_item_request).execute()
    except Exception as e:
        elapsed_time = datetime.now() - start_time
        log_and_print(f"Error uploading {os.path.basename(file_path)}: {e}, Hash: {file_hash}, Elapsed time: {elapsed_time}, {file_number}/{total_files}, {total_files}")
        time.sleep(2)
        return

    elapsed_time = datetime.now() - start_time
    log_message = f"{datetime.now()}, {file_path[-35:]}, {os.path.getsize(file_path)} bytes, Hash: {file_hash}, ctime: {time.ctime(os.path.getctime(file_path))}, mtime: {time.ctime(os.path.getmtime(file_path))}, this: {elapsed_time}, {file_number}/{total_files}"
    log_and_print(log_message)
    time.sleep(2)

def get_file_hash(file_path):
    with open(file_path, 'rb') as f:
        file_data = f.read()
    return hashlib.md5(file_data).hexdigest()

def scan_and_upload_folder(folder_path):
    file_paths = [os.path.join(root, file) for root, dirs, files in os.walk(folder_path) for file in files if
                  file.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'))]

    unprocessed_file_paths = []
    total_files = len(file_paths)
    log_and_print(f"Found {total_files} files to process.")

    for file_number, file_path in enumerate(file_paths, start=1):
        file_hash = get_file_hash(file_path)
        if file_hash not in uploaded_file_hashes:
            unprocessed_file_paths.append(file_path)
            log_and_print(f"Adding file {file_number} out of {total_files} to upload queue.")
        else:
            log_and_print(f"Skipping file {file_number} out of {total_files} (already processed).")

    total_files_to_upload = len(unprocessed_file_paths)
    log_and_print(f"Total new files to upload: {total_files_to_upload}")

    for file_number, file_path in enumerate(unprocessed_file_paths, start=1):
        upload_photo(file_path, file_number, total_files_to_upload)

# Use the variable in the function call
scan_and_upload_folder(folder_path_to_upload)

log_file.close()

# Now merge temporary log with the main log
with open(temp_log_file_path, 'r') as temp_log, open(log_file_path, 'a') as main_log:
    for line in temp_log:
        main_log.write(line)

# Remove temporary log file
os.remove(temp_log_file_path)
