#!/usr/bin/env python3

import requests
import os
from pathlib import Path

def download_japanese_font():
    """Download a free Japanese font for the game"""
    font_dir = Path(__file__).parent / "fonts"
    font_dir.mkdir(exist_ok=True)
    
    font_path = font_dir / "NotoSansJP-Regular.ttf"
    
    if font_path.exists():
        print(f"Font already exists: {font_path}")
        return str(font_path)
    
    # Use Google Fonts Noto Sans JP (lighter version)
    font_url = "https://fonts.gstatic.com/s/notosansjp/v52/nKKF-GM_FYFRJvXzVXaAPe97P2TF19naJhOgdxLUFONw.ttf"
    
    try:
        print("Downloading Japanese font...")
        response = requests.get(font_url, timeout=30)
        response.raise_for_status()
        
        with open(font_path, 'wb') as f:
            f.write(response.content)
        
        print(f"Japanese font downloaded: {font_path}")
        return str(font_path)
        
    except Exception as e:
        print(f"Failed to download font: {e}")
        return None

if __name__ == "__main__":
    download_japanese_font()