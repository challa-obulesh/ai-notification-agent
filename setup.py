"""
setup.py - One-click environment setup for AI Notification Agent
Runs: pip install, NLTK downloads, dataset generation, model training
"""

import subprocess, sys, os

def run(cmd, desc):
    print("\n" + "="*55)
    print("  " + desc)
    print("="*55)
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print("FAILED: " + desc)
        sys.exit(1)
    print("DONE: " + desc)

if __name__ == "__main__":
    print("\n[*] AI Notification Agent -- Setup")
    print("   Installing dependencies, generating data, and training model.")
    print("   Estimated time: 3-8 minutes.\n")

    # 1. Install packages
    run(
        f"{sys.executable} -m pip install -r requirements.txt --quiet",
        "Installing Python packages"
    )

    # 2. Download NLTK data
    run(
        f"{sys.executable} -c \"import nltk; [nltk.download(p, quiet=True) for p in ['punkt','punkt_tab','stopwords','wordnet','averaged_perceptron_tagger']]\"",
        "Downloading NLTK language data"
    )

    # 3. Generate dataset
    run(
        f"{sys.executable} data/notifications_dataset.py",
        "Generating 10,000-message notification dataset"
    )

    # 4. Train model
    run(
        f"{sys.executable} train_model.py",
        "Training ML classification model"
    )

    print("\n" + "="*55)
    print("  Setup complete!")
    print("  Run:  python app.py")
    print("  Then open:  http://localhost:5000")
    print("="*55 + "\n")
