"""
NEXUS Packaging Script
Creates a clean, complete, standalone ZIP archive containing all project files
ready for immediate upload to GitHub and deployment to Streamlit Cloud.
"""

import os
import zipfile
import shutil

SOURCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_ZIP_SCRATCH = os.path.abspath(os.path.join(SOURCE_DIR, "..", "nexus_project.zip"))
ARTIFACT_DIR = r"C:\Users\Muhammad Luqman\.gemini\antigravity\brain\7c6c8bb1-31c0-4533-86c9-4dc939a93cfd"
OUTPUT_ZIP_ARTIFACT = os.path.join(ARTIFACT_DIR, "nexus_project.zip")

EXCLUDE_PATTERNS = [
    "__pycache__",
    ".pyc",
    ".pytest_cache",
    ".DS_Store",
    "Thumbs.db",
    "nexus_project.zip"
]


def should_exclude(path: str) -> bool:
    base = os.path.basename(path)
    if base == ".git":
        return True
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path:
            return True
    return False


def build_zip():
    print(f"Creating ZIP archive from: {SOURCE_DIR}")
    
    # Target archive
    with zipfile.ZipFile(OUTPUT_ZIP_SCRATCH, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(SOURCE_DIR):
            # Prune excluded directories in-place
            dirs[:] = [d for d in dirs if not should_exclude(d)]
            
            for file in files:
                full_path = os.path.join(root, file)
                if should_exclude(full_path):
                    continue
                    
                rel_path = os.path.relpath(full_path, SOURCE_DIR)
                zf.write(full_path, rel_path)
                print(f" + {rel_path}")
                
    print(f"\n[SUCCESS] Successfully generated ZIP at: {OUTPUT_ZIP_SCRATCH}")
    
    # Also copy to artifact directory so it is directly downloadable
    try:
        os.makedirs(ARTIFACT_DIR, exist_ok=True)
        shutil.copy2(OUTPUT_ZIP_SCRATCH, OUTPUT_ZIP_ARTIFACT)
        print(f"[SUCCESS] Copied to Artifact Directory at: {OUTPUT_ZIP_ARTIFACT}")
    except Exception as e:
        print(f"[WARNING] Could not copy to artifact dir: {e}")
        
    # Verify archive contents
    print("\nVerifying archive integrity...")
    with zipfile.ZipFile(OUTPUT_ZIP_SCRATCH, "r") as zf:
        file_list = zf.namelist()
        print(f"Total files in archive: {len(file_list)}")
        assert "app.py" in file_list, "app.py missing from ZIP"
        assert "requirements.txt" in file_list, "requirements.txt missing from ZIP"
        assert "README.md" in file_list, "README.md missing from ZIP"
        assert ".streamlit/config.toml" in file_list, ".streamlit/config.toml missing from ZIP"
        print("Archive verified: All essential deployment files are present.")


if __name__ == "__main__":
    build_zip()
