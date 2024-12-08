import os
import requests
import tarfile
import zipfile
from io import BytesIO

OUTPUT_DIR = 'extracted_pypi_python_files'
os.makedirs(OUTPUT_DIR, exist_ok=True)

collected_files = set()

# Check for Python 3 features
def contains_python3_features(code):
    if "print " in code and not "print(" in code:
        return False # Likely Python 2 
    if "async " in code or "await " in code:
        return True # Python 3 feature
    if "f'" in code or 'f"' in code:
        return True # Python 3 feature
    return True

def fetch_metadata(package_name):
    url = f'https://pypi.org/pypi/{package_name}/json'
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch metadata for {package_name}. HTTP Status: {response.status_code}")
        return None

# Download and extract source
def process_distribution(url, package_name):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        file_like = BytesIO(response.content)

        # Extract files
        if url.endswith('.tar.gz') or url.endswith('.tgz'):
            with tarfile.open(fileobj=file_like, mode='r:gz') as tar:
                return extract_python_files(tar, package_name)
        elif url.endswith('.zip'):
            with zipfile.ZipFile(file_like) as zip_file:
                return extract_python_files(zip_file, package_name)
    except Exception as e:
        print(f"Error processing distribution: {e}")
        return []

def extract_python_files(archive, package_name):
    extracted_files = []
    for member in archive.namelist() if isinstance(archive, zipfile.ZipFile) else archive.getmembers():
        file_name = member.filename if isinstance(member, zipfile.ZipInfo) else member.name
        if file_name.endswith('.py'):
            unique_id = f"{package_name}:{file_name}"
            if unique_id in collected_files:
                continue # Skip duplicates
            
            content = (
                archive.read(member).decode('utf-8')
                if isinstance(archive, zipfile.ZipFile)
                else archive.extractfile(member).read().decode('utf-8')
            )
            if len(content) >= 500 and contains_python3_features(content):
                collected_files.add(unique_id)
                save_path = os.path.join(OUTPUT_DIR, f"code_snippet_pypi_{len(collected_files)}.py")
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                extracted_files.append(save_path)
                if len(collected_files) >= 500:
                    break
                
    return extracted_files

def collect_pypi_files(package_names):
    for package in package_names:
        if len(collected_files) >= 500:
            break
        print(f"Processing package: {package}")
        metadata = fetch_metadata(package)

        if metadata and 'urls' in metadata:
            for url_info in metadata['urls']:
                if url_info['packagetype'] == 'sdist':
                    print(f"Downloading and processing: {url_info['url']}")
                    process_distribution(url_info['url'], package)
                    if len(collected_files) >= 500:
                        break

    print(f"Total Python 3 files collected: {len(collected_files)}")

if __name__ == '__main__':
    example_packages = ['requests', 'numpy', 'pandas', 'scipy', 'matplotlib', 'flask', 'django', 'torch', 'tensorflow']
    collect_pypi_files(example_packages)
