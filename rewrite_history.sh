#!/bin/bash
# Download git-filter-repo if not present
if [ ! -f git-filter-repo.py ]; then
    curl -o git-filter-repo.py https://raw.githubusercontent.com/newren/git-filter-repo/main/git-filter-repo
fi
python git-filter-repo.py --mailmap author_mailmap.txt --force
