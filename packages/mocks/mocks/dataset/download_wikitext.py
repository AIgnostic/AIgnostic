# download_wikitext.py
from datasets import load_dataset

print("Downloading WikiText-103 dataset...")
load_dataset("wikitext", "wikitext-103-raw-v1")
print("Dataset downloaded successfully.")