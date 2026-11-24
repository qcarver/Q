#!/usr/bin/env bash
set -euo pipefail

project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
document_root=${Q_GRANVILLE_ROOT:-/var/www/html}

if [[ ! -d "$document_root" || ! -w "$document_root" || "$document_root" == / ]]; then
  printf 'Refusing unsafe or unwritable document root: %s\n' "$document_root" >&2
  exit 1
fi

mkdir -p "$project_root/build"
exec 9>"$project_root/build/.granville-deploy.lock"
flock -n 9 || exit 0

cd "$project_root"
python3 -m generator --target lan

if find build/lan -type l -print -quit | grep -q .; then
  echo 'Refusing LAN artifact containing a symbolic link' >&2
  exit 1
fi

rsync -a --delete --exclude='.well-known/' build/lan/ "$document_root/"
printf 'Deployed Überproject-Q to %s\n' "$document_root"
