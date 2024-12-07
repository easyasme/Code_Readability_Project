import os
import requests
import time

GITHUB_TOKEN = ''

# Headers for authentication
headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3.text-match+json',
}

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

# Download file content
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

def collect_code_snippets(max_files=10):
    query = 'language:Python size:>1000'  # Bytes
    page = 1
    per_page = 100
    total_collected = 0

    output_directory = 'extracted_codes_python3'
    os.makedirs(output_directory, exist_ok=True)

    while total_collected < max_files:
        print(f'Searching page {page}')
        result = search_code(query, per_page=per_page, page=page)

        if result and 'items' in result:
            for item in result['items']:
                file_url = item['html_url']
                raw_url = file_url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
                code = download_file(raw_url)

                if code and contains_python3_features(code):
                    total_collected += 1
                    file_name = f'code_snippet_{total_collected}.py'
                    file_path = os.path.join(output_directory, file_name)

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(code)

                    print(f'Collected {total_collected} Python 3-compatible files: {file_name}')
                    if total_collected >= max_files:
                        break
                time.sleep(1)
            page += 1
            if page > 10:  # GitHub limits = 1000 results total
                break
        else:
            break

    print(f'Total Python 3 code snippets collected: {total_collected}')

if __name__ == '__main__':
    collect_code_snippets(max_files=500)
