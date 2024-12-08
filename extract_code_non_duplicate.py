import os
import requests
import time
import hashlib

GITHUB_TOKEN = ''

# Headers for authentication
headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3.text-match+json',
}

# Compute a hash to track unique files
def compute_hash(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()

# Search for Python files
def search_code(query, per_page=100, page=1):
    url = 'https://api.github.com/search/code'
    params = {
        'q': query,
        'per_page': per_page,
        'page': page,
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error {response.status_code}: {response.json()}')
        return None

def download_file(url):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f'Error {response.status_code}: {response.json()}')
        return None

# Check for Python 3 features
def contains_python3_features(code):
    if "print " in code and not "print(" in code:
        return False  # Python 2 due to `print` statement
    if "async " in code or "await " in code:
        return True  # Python 3 feature
    if "f'" in code or 'f"' in code:
        return True  # Python 3 feature
    return True

def collect_code_snippets(max_files=500):
    query = 'language:Python size:>1000'  # Bytes
    page = 1
    per_page = 100

    output_directory = 'extracted_codes_python3'
    os.makedirs(output_directory, exist_ok=True)

    # Get existing files and identify missing numbers
    existing_files = [
        int(f.split('_')[2].split('.')[0]) 
        for f in os.listdir(output_directory) 
        if f.startswith('code_snippet_') and f.endswith('.py')
    ]
    missing_numbers = sorted(set(range(1, max_files + 1)) - set(existing_files))
    total_collected = len(existing_files)

    collected_hashes = {
        compute_hash(open(os.path.join(output_directory, f), 'r', encoding='utf-8').read())
        for f in os.listdir(output_directory) 
        if f.startswith('code_snippet_') and f.endswith('.py')
    }

    while missing_numbers:
        print(f'Searching page {page}')
        result = search_code(query, per_page=per_page, page=page)

        if result and 'items' in result:
            for item in result['items']:
                if not missing_numbers:
                    break

                file_url = item['html_url']
                raw_url = file_url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
                code = download_file(raw_url)

                if code and contains_python3_features(code):
                    code_hash = compute_hash(code)
                    if code_hash in collected_hashes:
                        print("Duplicate file detected, skipping...")
                        continue

                    collected_hashes.add(code_hash)
                    next_missing_number = missing_numbers.pop(0)
                    file_name = f'code_snippet_{next_missing_number}.py'
                    file_path = os.path.join(output_directory, file_name)

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(code)

                    total_collected += 1
                    print(f'Collected {total_collected} Python 3-compatible files: {file_name}')
                time.sleep(1)
            page += 1
            if page > 10:  # GitHub limits = 1000 results total
                break
        else:
            break

    print(f'Total Python 3 code snippets collected: {total_collected}')

if __name__ == '__main__':
    collect_code_snippets(max_files=500)
