"""
Automated Hugging Face Spaces Deployer
Usage:
    python deploy_hf.py --username <HF_USERNAME> --token <HF_WRITE_TOKEN>
    or run interactively:
    python deploy_hf.py
"""

import os
import sys
import argparse
from huggingface_hub import HfApi

def deploy(username, token, space_name="credit-card-fraud-detection"):
    repo_id = f"{username}/{space_name}"
    print(f"\n[1/3] Authenticating with Hugging Face...")
    api = HfApi(token=token)
    
    print(f"[2/3] Initializing Space: https://huggingface.co/spaces/{repo_id} ...")
    try:
        api.create_repo(
            repo_id=repo_id,
            repo_type="space",
            space_sdk="streamlit",
            space_hardware="cpu-basic",
            exist_ok=True
        )
    except Exception as e:
        print(f"Space initialization note: {e}")

    files_to_deploy = [
        "streamlit_app.py",
        "requirements.txt",
        "credit_fraud.pkl",
        "image.png",
        "README.md"
    ]

    print(f"[3/3] Uploading deployment artifacts...")
    for filename in files_to_deploy:
        if os.path.exists(filename):
            print(f"  -> Uploading {filename}...")
            api.upload_file(
                path_or_fileobj=filename,
                path_in_repo=filename,
                repo_id=repo_id,
                repo_type="space"
            )
        else:
            print(f"  -> Skipping missing file: {filename}")

    print("\n" + "=" * 60)
    print("🚀 Deployment Complete!")
    print(f"Live Space URL: https://huggingface.co/spaces/{repo_id}")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy to Hugging Face Spaces")
    parser.add_argument("--username", help="Hugging Face Username", default="")
    parser.add_argument("--token", help="Hugging Face Write Token", default="")
    parser.add_argument("--name", help="Space Name", default="credit-card-fraud-detection")
    args = parser.parse_args()

    username = args.username
    token = args.token

    if not username:
        username = input("Enter your Hugging Face username: ").strip()
    if not token:
        token = input("Enter your Hugging Face Write Token (get it from https://huggingface.co/settings/tokens): ").strip()

    if not username or not token:
        print("Error: Both username and write token are required for deployment.")
        sys.exit(1)

    deploy(username=username, token=token, space_name=args.name)
