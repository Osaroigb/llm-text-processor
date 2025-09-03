"""
Script to download required NLTK data for the LLM Text Processor.
Run this script before running tests or using the NLP utilities.
"""

import nltk
import sys

def download_nltk_data():
    """Download required NLTK data packages."""
    print("Downloading required NLTK data...")
    
    required_packages = [
        'punkt',
        'averaged_perceptron_tagger', 
        'stopwords',
        'wordnet'
    ]
    
    for package in required_packages:
        try:
            print(f"Downloading {package}...")
            nltk.download(package, quiet=True)
            print(f"✓ {package} downloaded successfully")
        except Exception as e:
            print(f"✗ Failed to download {package}: {e}")
            return False
    
    print("\nAll NLTK data downloaded successfully!")
    return True

if __name__ == "__main__":
    success = download_nltk_data()
    sys.exit(0 if success else 1)
