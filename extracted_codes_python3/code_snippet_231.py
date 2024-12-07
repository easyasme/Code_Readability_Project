no import boto3
from botocore.client import Config

# Initialize the session
session = boto3.session.Session()

# S3 client for Hitachi Vantara's S3-compatible service
s3_client = session.client(
    's3',
    endpoint_url='https://your-hitachi-vantara-s3-endpoint.com',  # Replace with your endpoint
    aws_access_key_id='your-access-key',                          # Replace with your access key
    aws_secret_access_key='your-secret-key',                      # Replace with your secret key
    config=Config(signature_version='s3v4')  # Ensure S3v4 signature is used
)

# Function to create a folder in S3
def create_folder(bucket_name, folder_name):
    # Folders are represented as objects with '/' at the end of the key
    folder_key = folder_name if folder_name.endswith('/') else folder_name + '/'
    
    # Create the folder by uploading a zero-byte object with the folder name
    s3_client.put_object(Bucket=bucket_name, Key=folder_key)
    print(f"Folder '{folder_name}' created in bucket '{bucket_name}'")

# Example usage
bucket_name = 'your-bucket-name'  # Replace with your S3 bucket name
folder_name = 'my-folder/sub-folder'  # Replace with the folder path you want to create

# Create the folder
create_folder(bucket_name, folder_name)


##################

import boto3
from botocore.client import Config

# Initialize the S3 client for Hitachi Vantara's S3-compatible service
s3_client = boto3.client(
    's3',
    endpoint_url='https://your-hitachi-vantara-s3-endpoint.com',  # Replace with your endpoint
    aws_access_key_id='your-access-key',                          # Replace with your access key
    aws_secret_access_key='your-secret-key',                      # Replace with your secret key
    config=Config(signature_version='s3v4'),
    verify=False  # Disable SSL verification if needed
)

# Function to upload a file to a specific folder
def upload_file_to_folder(bucket_name, folder_name, file_path, object_name=None):
    # Ensure the folder name ends with a slash ('/') to specify a folder path
    folder_key = folder_name if folder_name.endswith('/') else folder_name + '/'
    
    # Object name is the file name if not provided
    if object_name is None:
        object_name = file_path.split('/')[-1]  # Extract the file name from the file path
    
    # Full key will include the folder path and the object (file) name
    key = folder_key + object_name
    
    # Upload the file
    s3_client.upload_file(file_path, bucket_name, key)
    print(f"File '{file_path}' uploaded to folder '{folder_name}' in bucket '{bucket_name}' as '{key}'")

# Example usage
bucket_name = 'your-bucket-name'  # Replace with your S3 bucket name
folder_name = 'my-folder/sub-folder'  # Replace with the folder path you want to upload to
file_path = '/path/to/your/local/file.txt'  # Replace with the path to your local file
object_name = 'custom_file_name.txt'  # Optional: Replace with a custom name for the uploaded object

# Upload the file to the specific folder
upload_file_to_folder(bucket_name, folder_name, file_path, object_name)
####################################

import boto3
from botocore.client import Config
import yaml

# Function to load YAML config
def load_yaml_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Load connection parameters from the connection_config.yaml file
connection_config = load_yaml_config('connection_config.yaml')

# Load permissions configuration from permissions_config.yaml file
permissions_config = load_yaml_config('permissions_config.yaml')

# Initialize the S3 client using connection details from the config file
s3_client = boto3.client(
    's3',
    endpoint_url=connection_config['connection']['endpoint_url'],
    aws_access_key_id=connection_config['connection']['aws_access_key_id'],
    aws_secret_access_key=connection_config['connection']['aws_secret_access_key'],
    config=Config(signature_version='s3v4'),
    verify=connection_config['connection']['verify_ssl']
)

# Function to set ACL based on the role (can be applied to users or groups)
def set_acl_by_role(bucket_name, key, target_id, role, is_group=False):
    if role == 'read':
        grant = f'uri="http://acs.amazonaws.com/groups/global/AllUsers"' if is_group else f'id="{target_id}"'
        s3_client.put_object_acl(Bucket=bucket_name, Key=key, GrantRead=grant)
        entity_type = "Group" if is_group else "User"
        print(f"Read permission set for {entity_type} '{target_id}' on object '{key}'")
    
    elif role == 'write':
        grant = f'uri="http://acs.amazonaws.com/groups/global/AllUsers"' if is_group else f'id="{target_id}"'
        s3_client.put_object_acl(Bucket=bucket_name, Key=key, GrantWrite=grant)
        entity_type = "Group" if is_group else "User"
        print(f"Write permission set for {entity_type} '{target_id}' on object '{key}'")
    
    elif role == 'full-control':
        grant = f'uri="http://acs.amazonaws.com/groups/global/AllUsers"' if is_group else f'id="{target_id}"'
        s3_client.put_object_acl(Bucket=bucket_name, Key=key, GrantFullControl=grant)
        entity_type = "Group" if is_group else "User"
        print(f"Full control granted to {entity_type} '{target_id}' on object '{key}'")
    
    else:
        raise ValueError(f"Invalid role specified: {role}")

# Function to apply folder-level permissions
def apply_folder_permissions(bucket_name, folder_permissions):
    folder_name = folder_permissions['folder_name']
    
    # Ensure the folder name ends with a slash ('/') to specify it's a folder
    folder_key = folder_name if folder_name.endswith('/') else folder_name + '/'
    
    for group in folder_permissions['groups']:
        group_id = group['group_id']
        role = group['role']
        # Set permissions for each group on the folder
        set_acl_by_role(bucket_name, folder_key, group_id, role, is_group=True)

# Function to upload files and apply individual object permissions
def upload_files_and_set_permissions():
    bucket_name = permissions_config['permissions']['bucket_name']
    
    # Apply folder-level permissions
    folder_permissions = permissions_config['permissions'].get('folder_permissions')
    if folder_permissions:
        apply_folder_permissions(bucket_name, folder_permissions)
    
    # Apply object-specific permissions
    objects = permissions_config['permissions']['objects']
    for obj in objects:
        object_name = obj['object_name']
        target_user_id = obj['target_user_id']
        role = obj['role']

        # Upload the file (path assumed to be local object_name for simplicity)
        s3_client.upload_file(object_name, bucket_name, object_name)
        print(f"File '{object_name}' uploaded to bucket '{bucket_name}' as '{object_name}'")

        # Set permissions for the uploaded object
        set_acl_by_role(bucket_name, object_name, target_user_id, role)

# Run the upload and permission setting
upload_files_and_set_permissions()

###########################

permissions.ymal

permissions:
  bucket_name: "your-bucket-name"
  
  # Folder-level permissions
  folder_permissions:
    folder_name: "my-folder/sub-folder"
    groups:
      - group_id: "group1-canonical-id"
        role: "read"
      - group_id: "group2-canonical-id"
        role: "full-control"

  # Object-specific permissions
  objects:
    - object_name: "file1.txt"
      target_user_id: "user1-canonical-id"
      role: "read"

    - object_name: "file2.txt"
      target_user_id: "user2-canonical-id"
      role: "write"
    
#####################
connection.yaml

connection:
  endpoint_url: "https://your-hitachi-vantara-s3-endpoint.com"
  aws_access_key_id: "your-access-key"
  aws_secret_access_key: "your-secret-key"
  verify_ssl: false

######################

import boto3
from botocore.client import Config

# Replace with your HCP details
HCP_ACCESS_KEY = "your-access-key"
HCP_SECRET_KEY = "your-secret-key"
HCP_DOMAIN = "your-hcp-domain.com"  # e.g., "hcp.example.com"
BUCKET_NAME = "your-bucket-name"
OBJECT_KEY = "your-object-key"  # Path to the object within the bucket

# Initialize the boto3 client for S3 with HCP endpoint
s3_client = boto3.client(
    's3',
    aws_access_key_id=HCP_ACCESS_KEY,
    aws_secret_access_key=HCP_SECRET_KEY,
    endpoint_url=f"https://{HCP_DOMAIN}",
    config=Config(s3={'addressing_style': 'path'})
)

# Retrieve the ACL for the specified object
try:
    acl_response = s3_client.get_object_acl(Bucket=BUCKET_NAME, Key=OBJECT_KEY)

    # Print the ACL details
    print("ACLs for the object:")
    for grant in acl_response['Grants']:
        grantee = grant['Grantee']
        permission = grant['Permission']
        grantee_type = grantee['Type']
        
        # Print grantee details and permissions
        if grantee_type == 'CanonicalUser':
            print(f"User: {grantee['DisplayName']}, Permission: {permission}")
        elif grantee_type == 'Group':
            print(f"Group: {grantee['URI']}, Permission: {permission}")

except s3_client.exceptions.NoSuchKey:
    print("The specified object does not exist.")
except s3_client.exceptions.ClientError as e:
    print(f"Failed to retrieve ACLs: {e}")


####### list all ACLS AND Id's ######

import boto3
from botocore.client import Config

# Replace with your HCP credentials and bucket information
HCP_ACCESS_KEY = "your-access-key"
HCP_SECRET_KEY = "your-secret-key"
HCP_DOMAIN = "your-hcp-domain.com"
BUCKET_NAME = "your-bucket-name"

# Initialize the boto3 client for S3 with HCP endpoint
s3_client = boto3.client(
    's3',
    aws_access_key_id=HCP_ACCESS_KEY,
    aws_secret_access_key=HCP_SECRET_KEY,
    endpoint_url=f"https://{HCP_DOMAIN}",
    config=Config(s3={'addressing_style': 'path'})
)

# List all objects in the bucket
response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)

if 'Contents' in response:
    for obj in response['Contents']:
        object_key = obj['Key']
        print(f"\nObject Key: {object_key}")

        # Retrieve the ACL for each object
        acl_response = s3_client.get_object_acl(Bucket=BUCKET_NAME, Key=object_key)
        print("ACLs for this object:")
        for grant in acl_response['Grants']:
            grantee = grant['Grantee']
            permission = grant['Permission']
            grantee_type = grantee['Type']

            # Print grantee details and permissions
            if grantee_type == 'CanonicalUser':
                print(f"User: {grantee.get('DisplayName', 'N/A')}, ID: {grantee['ID']}, Permission: {permission}")
            elif grantee_type == 'Group':
                print(f"Group: {grantee.get('URI', 'N/A')}, Permission: {permission}")
else:
    print("No objects found in the bucket.")

###### list users ####

import requests
from requests.auth import HTTPBasicAuth

# Replace with your HCP details
HCP_DOMAIN = "your-hcp-domain.com"  # e.g., "hcp.example.com"
HCP_USERNAME = "admin-username"      # Administrator username
HCP_PASSWORD = "admin-password"       # Administrator password

# URL to retrieve the list of users
url = f"https://{HCP_DOMAIN}/management/v1/users"

try:
    # Send GET request to retrieve users
    response = requests.get(url, auth=HTTPBasicAuth(HCP_USERNAME, HCP_PASSWORD))

    # Check if the request was successful
    if response.status_code == 200:
        users = response.json()  # Parse JSON response
        user_list = []

        # Collect just the user IDs or display names
        for user in users['users']:
            user_list.append(user['displayName'])  # or user['id'] for user IDs

        # Print the list of users
        print("List of Users in the Environment:")
        print("\n".join(user_list))
    else:
        print(f"Failed to retrieve users. Status Code: {response.status_code}")
        print(f"Error Message: {response.text}")

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
    
    
    ###### deleating files ######
    
import boto3
from botocore.client import Config
import yaml

# Function to load YAML config
def load_yaml_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Load connection parameters from the connection_config.yaml file
connection_config = load_yaml_config('connection_config.yaml')

# Initialize the S3 client using connection details from the config file
s3_client = boto3.client(
    's3',
    endpoint_url=connection_config['connection']['endpoint_url'],
    aws_access_key_id=connection_config['connection']['aws_access_key_id'],
    aws_secret_access_key=connection_config['connection']['aws_secret_access_key'],
    config=Config(signature_version='s3v4'),
    verify=connection_config['connection']['verify_ssl']
)

# Function to delete a file from the target S3 location
def delete_file(bucket_name, object_key):
    try:
        # Delete the file
        s3_client.delete_object(Bucket=bucket_name, Key=object_key)
        print(f"File '{object_key}' successfully deleted from bucket '{bucket_name}'")
    except s3_client.exceptions.NoSuchKey:
        print(f"The file '{object_key}' does not exist in bucket '{bucket_name}'")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
bucket_name = "your-bucket-name"  # Replace with your S3 bucket name
object_key = "my-folder/sub-folder/file_to_delete.txt"  # Replace with the file's key (path in the bucket)

# Call the delete function
delete_file(bucket_name, object_key)
