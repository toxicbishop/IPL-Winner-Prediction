"""Download the latest Cricsheet IPL JSON archive and extract it into data/raw_datasets/ipl/."""

import io
import urllib.request
import zipfile
from pathlib import Path

URL = "https://cricsheet.org/downloads/ipl_json.zip"
DEST = Path(__file__).resolve().parent.parent / "data" / "raw_datasets" / "ipl"


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {URL}")
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        buf = io.BytesIO(resp.read())
    print(f"Downloaded {buf.getbuffer().nbytes / 1_000_000:.1f} MB")

    with zipfile.ZipFile(buf) as zf:
        before = {p.name for p in DEST.glob("*.json")}
        zf.extractall(DEST)
        after = {p.name for p in DEST.glob("*.json")}

    new = sorted(after - before)
    print(f"Total match files: {len(after)}  (new: {len(new)})")
    for name in new:
        print(f"  + {name}")


if __name__ == "__main__":
    main()
