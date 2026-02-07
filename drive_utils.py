import os.path
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from config import GOOGLE_DRIVE_FOLDER_NAME

# If modifying scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

import logging
logger = logging.getLogger(__name__)

class GoogleDriveManager:
    def __init__(self, credentials_file='client_secrets.json', token_file='token.json'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        # self.authenticate() # Removed initial authentication call

    def authenticate(self):
        """Authenticates or refreshes the Drive service."""
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("Drive token refreshed.")
                except Exception as e:
                    logger.error(f"Error refreshing Drive token: {e}")
                    creds = None
            
            if not creds:
                if os.path.exists(self.credentials_file):
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_file, SCOPES)
                        # open_browser=False is safer for potentially headless environments
                        creds = flow.run_local_server(port=0, open_browser=False)
                        
                        # Save the credentials for the next run
                        with open(self.token_file, 'w') as token:
                            token.write(creds.to_json())
                    except Exception as e:
                        logger.error(f"Drive auth failed: {e}")
                        return False

        if creds:
            try:
                # Always build a fresh service to avoid stale connections
                self.service = build('drive', 'v3', credentials=creds)
                return True
            except Exception as e:
                logger.error(f"Failed to build Drive service: {e}")
        return False

    def _ensure_service(self):
        """Ensures the service is initialized and authenticated."""
        if not self.service:
            return self.authenticate()
        # Check if token is still valid (simplified check)
        return True

    def upload_file(self, filename, mimetype=None):
        """Uploads or updates a file on Google Drive."""
        self.authenticate() # Ensure fresh session
        if not self.service:
            print("Drive service unavailable.")
            return None

        if not os.path.exists(filename):
            print(f"File {filename} not found.")
            return None

        import time
        for attempt in range(3):
            try:
                print(f"Drive upload attempt {attempt+1} for {filename}...")
                file_metadata = {'name': os.path.basename(filename)}
                
                # Determine mimetype if not provided
                if not mimetype:
                    if filename.lower().endswith('.xlsx'):
                        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    elif filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
                        mimetype = 'image/jpeg'
                    elif filename.lower().endswith('.png'):
                        mimetype = 'image/png'
                    elif filename.lower().endswith('.pdf'):
                        mimetype = 'application/pdf'
                    else:
                        mimetype = 'application/octet-stream'

                # Use BytesIO to avoid locking the file
                with open(filename, 'rb') as f:
                    file_content = io.BytesIO(f.read())
                
                media = MediaIoBaseUpload(file_content, mimetype=mimetype, resumable=True)

                # Check if file already exists in the specific folder
                folder_name = GOOGLE_DRIVE_FOLDER_NAME
                folder_query = f"mimeType = 'application/vnd.google-apps.folder' and name = '{folder_name}' and trashed = false"
                folder_results = self.service.files().list(q=folder_query, fields="files(id, name)", pageSize=1).execute()
                folders = folder_results.get('files', [])
                
                parent_id = None
                if folders:
                    parent_id = folders[0]['id']
                else:
                    folder_metadata = {
                        'name': folder_name,
                        'mimeType': 'application/vnd.google-apps.folder'
                    }
                    folder = self.service.files().create(body=folder_metadata, fields='id').execute()
                    parent_id = folder.get('id')
                    print(f"Created folder '{folder_name}' with ID: {parent_id}")

                query = f"name = '{os.path.basename(filename)}' and '{parent_id}' in parents and trashed = false"
                results = self.service.files().list(q=query, fields="files(id, name, webViewLink)").execute()
                items = results.get('files', [])

                file_metadata['parents'] = [parent_id]

                if not items:
                    file = self.service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
                    print(f'File ID: {file.get("id")} created.')
                    return file.get('webViewLink')
                else:
                    file_id = items[0]['id']
                    self.service.files().delete(fileId=file_id).execute()
                    print(f"Deleted old file {file_id}. Uploading new one...")
                    
                    file = self.service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
                    print(f'File ID: {file.get("id")} created (replaced).')
                    return file.get('webViewLink')

            except Exception as e:
                print(f"Drive upload attempt {attempt+1} failed: {e}")
                if attempt < 2:
                    time.sleep(1)
                else:
                    return None
        return None

    def delete_file_by_name(self, filename):
        """Finds and deletes a file by name in the specific folder."""
        self.authenticate()
        if not self.service: return False
        try:
            folder_name = GOOGLE_DRIVE_FOLDER_NAME
            # Find folder
            folder_results = self.service.files().list(
                q=f"mimeType = 'application/vnd.google-apps.folder' and name = '{folder_name}' and trashed = false",
                fields="files(id)", pageSize=1
            ).execute()
            folders = folder_results.get('files', [])
            if not folders: return False
            parent_id = folders[0]['id']

            # Find file in folder
            query = f"name = '{filename}' and '{parent_id}' in parents and trashed = false"
            results = self.service.files().list(q=query, fields="files(id)").execute()
            items = results.get('files', [])

            for item in items:
                self.service.files().delete(fileId=item['id']).execute()
                print(f"Deleted file {filename} (ID: {item['id']})")
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

    def clear_folder_contents(self):
        """Deletes all files in the configured Drive folder."""
        self.authenticate()
        if not self.service: return False
        try:
            folder_name = GOOGLE_DRIVE_FOLDER_NAME
            # Find folder
            folder_results = self.service.files().list(
                q=f"mimeType = 'application/vnd.google-apps.folder' and name = '{folder_name}' and trashed = false",
                fields="files(id)", pageSize=1
            ).execute()
            folders = folder_results.get('files', [])
            if not folders: return False
            parent_id = folders[0]['id']

            # List all files in folder
            query = f"'{parent_id}' in parents and trashed = false"
            results = self.service.files().list(q=query, fields="files(id, name)").execute()
            items = results.get('files', [])

            for item in items:
                self.service.files().delete(fileId=item['id']).execute()
                print(f"Deleted file {item['name']} (ID: {item['id']}) from Drive.")
            return True
        except Exception as e:
            print(f"Error clearing Drive folder: {e}")
            return False
