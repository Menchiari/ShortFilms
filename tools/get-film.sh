#!/bin/sh
# Check out one more film in a sparse clone:  sh tools/get-film.sh 001
# First time on a computer (light clone, nothing heavy downloaded):
#   git clone --filter=blob:none --sparse https://github.com/Menchiari/ShortFilms.git ~/ShortFilms
#   cd ~/ShortFilms && git sparse-checkout set tools templates docs && sh tools/get-film.sh 001
set -e
[ -n "$1" ] || { echo "usage: sh tools/get-film.sh <film id, e.g. 001>"; exit 1; }
cd "$(git rev-parse --show-toplevel)"
id=$(printf "%03d" "$1" 2>/dev/null || echo "$1")
name=$(git ls-tree -d --name-only HEAD films/ | sed 's|^films/||' | grep "^$id-" | head -n 1)
[ -n "$name" ] || { echo "No film starting with $id- on this branch."; exit 1; }
if [ "$(git config core.sparseCheckout)" = "true" ]; then
  git sparse-checkout add "films/$name"
else
  echo "This clone is complete already, films/$name is here."
fi
echo "Ready: films/$name"
