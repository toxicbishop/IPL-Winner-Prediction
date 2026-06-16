#!/bin/bash

# This script changes all commits authored by dependabot to be authored and committed by toxicbishop.

git filter-branch -f --env-filter '
if [ "$GIT_AUTHOR_NAME" = "dependabot[bot]" ];
then
    export GIT_AUTHOR_NAME="toxicbishop"
    export GIT_AUTHOR_EMAIL="92860129+toxicbishop@users.noreply.github.com"
    export GIT_COMMITTER_NAME="toxicbishop"
    export GIT_COMMITTER_EMAIL="92860129+toxicbishop@users.noreply.github.com"
fi
' --tag-name-filter cat -- --branches --tags
