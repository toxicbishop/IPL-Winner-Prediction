import os

import requests

logos = {
    "t20_wc_2026": "https://upload.wikimedia.org/wikipedia/commons/f/f8/2026_ICC_Men%27s_T20_World_Cup_logo.png",
    "india": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Board_of_Control_for_Cricket_in_India_Logo_%282024%29.svg/1200px-Board_of_Control_for_Cricket_in_India_Logo_%282024%29.svg.png",
    "pakistan": "https://upload.wikimedia.org/wikipedia/commons/5/53/Pakistan_cricket_team_logo.png",
    "australia": "https://upload.wikimedia.org/wikipedia/en/5/5e/Cricket_Australia.png",
    "england": "https://upload.wikimedia.org/wikipedia/en/thumb/c/ce/England_Cricket_Team_Logo.svg/1200px-England_Cricket_Team_Logo.svg.png",
    "south_africa": "https://upload.wikimedia.org/wikipedia/en/thumb/4/4f/Cricket_South_Africa.svg/1200px-Cricket_South_Africa.svg.png",
    "new_zealand": "https://upload.wikimedia.org/wikipedia/en/e/e1/NZCricket.png",
    "west_indies": "https://upload.wikimedia.org/wikipedia/en/thumb/9/9b/West_Indies_Cricket_Board_Logo.svg/1200px-West_Indies_Cricket_Board_Logo.svg.png",
    "sri_lanka": "https://upload.wikimedia.org/wikipedia/en/thumb/d/d4/Flag_of_Sri_Lanka_Cricket.svg/1200px-Flag_of_Sri_Lanka_Cricket.svg.png",
    "afghanistan": "https://upload.wikimedia.org/wikipedia/en/0/01/Afghanistan_Cricket_Board_logo.jpg",
    "bangladesh": "https://upload.wikimedia.org/wikipedia/en/thumb/3/3d/Bangladesh_Cricket_Board_Logo.svg/1200px-Bangladesh_Cricket_Board_Logo.svg.png",
}

output_dir = os.path.join("data", "assets", "logos")
os.makedirs(output_dir, exist_ok=True)

for name, url in logos.items():
    try:
        print(f"Downloading {name}...")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, stream=True, timeout=10, headers=headers)
        if response.status_code == 200:
            ext = ".png" if "png" in url.lower() or "svg" in url.lower() else ".jpg"
            file_path = os.path.join(output_dir, f"{name}{ext}")
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Successfully downloaded {name} to {file_path}")
        else:
            print(f"Failed to download {name}: HTTP {response.status_code}")
    except Exception as e:
        print(f"Error downloading {name}: {e}")
