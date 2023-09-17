from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import requests
import os
import time
import hashlib
from datetime import datetime

# Initialize the log file
log_file = open('upload_log.txt', 'a')


def log_and_print(message):
    print(message)
    log_file.write(message + '\n')


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

    with open(file_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()

    file_name_without_extension = os.path.splitext(os.path.basename(file_path))[0]
    description = f"Description for {file_name_without_extension}, Hash: {file_hash}"

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

    elapsed_time = datetime.now() - start_time
    log_message = f"{datetime.now()}, {os.path.basename(file_path)}, {os.path.getsize(file_path)} bytes, {time.ctime(os.path.getctime(file_path))}, {time.ctime(os.path.getmtime(file_path))}, {time.ctime(os.path.getatime(file_path))}, {elapsed_time}, {file_number}/{total_files}, {total_files}"
    log_and_print(log_message)


def scan_and_upload_folder(folder_path):
    file_paths = [os.path.join(root, file) for root, dirs, files in os.walk(folder_path) for file in files if
                  file.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'))]
    total_files = len(file_paths)

    for file_number, file_path in enumerate(file_paths, start=1):
        upload_photo(file_path, file_number, total_files)


# Replace with your folder path
# scan_and_upload_folder(r'C:\Users\karl_\Downloads\TEST_GCP_UPLOADS')
scan_and_upload_folder(r'D:\RECOVERY\PICS_VIDEOS\FAMILY')

log_file.close()
