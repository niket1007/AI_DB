import os
import requests
import tarfile

def download_file(url, filename):
    print(f"Downloading {filename}...")
    response = requests.get(url, stream=True)
    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print("Download complete.")

def setup_wikisql():
    # Create directory
    os.makedirs("wikisql", exist_ok=True)
    
    # WikiSQL is hosted on GitHub by Salesforce
    base_url = "https://github.com/salesforce/WikiSQL/raw/master/data.tar.bz2"
    tar_path = "wikisql/data.tar.bz2"
    
    if not os.path.exists(tar_path):
        download_file(base_url, tar_path)
    
    print("Extracting files...")
    with tarfile.open(tar_path, "r:bz2") as tar:
        tar.extractall(path="wikisql")
    
    # Cleanup: Move files from data subfolder to wikisql root if necessary
    # The tar contains a folder named 'data'
    data_dir = "wikisql/data"
    if os.path.exists(data_dir):
        for file in os.listdir(data_dir):
            os.rename(os.path.join(data_dir, file), os.path.join("wikisql", file))
        os.rmdir(data_dir)
    
    print("\nSuccess! Files available in ./wikisql/")
    print("Required for Evaluator:")
    print("- wikisql/dev.jsonl")
    print("- wikisql/dev.tables.jsonl")

if __name__ == "__main__":
    setup_wikisql()