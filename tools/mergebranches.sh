#!/usr/bin/env bash
# Merge every branch pushed in the last 48 hours that is ahead of main and changes only content
# (stories/, films/, films-index.json) into the current checkout of main. Run by film-sync.yml;
# the caller pushes. A branch that would change anything else, fails `filmtool check` or has a
# real conflict is left alone and named in the output (it needs a person or a pull request). An
# older unmerged branch is named when it holds take files main does not have.
set -u
git config merge.filmjson.driver "python3 tools/jsonmerge.py %O %A %B"
git config merge.keep.driver true
git fetch -q origin '+refs/heads/*:refs/remotes/origin/*'
now=$(date +%s)
for ref in $(git for-each-ref --sort=committerdate --format='%(refname:short)' refs/remotes/origin/); do
  b=${ref#origin/}
  case "$b" in main|HEAD|origin) continue ;; esac
  git merge-base --is-ancestor "$ref" HEAD && continue
  if [ $(( now - $(git log -1 --format=%ct "$ref") )) -ge 172800 ]; then
    # too old to merge on its own: name it when it holds take files main does not have
    lost=$(git ls-tree -r --name-only "$ref" -- films | grep '/05-generation/takes/' \
      | grep -cvxFf <(git ls-tree -r --name-only HEAD -- films | grep '/05-generation/takes/'))
    [ "$lost" -gt 0 ] && echo "NOT CHECKED $b: last push over 48 hours ago, $lost take files main does not have"
    continue
  fi
  before=$(git rev-parse HEAD)
  if ! git merge -q --no-ff --no-edit -m "content: merge $b" "$ref" >/dev/null 2>&1; then
    echo "NOT MERGED $b: conflict in $(git diff --name-only --diff-filter=U | tr '\n' ' ')"
    git merge --abort
    continue
  fi
  other=$(git diff --name-only "$before" HEAD | grep -v -e '^stories/' -e '^films/' -e '^films-index\.json$' || true)
  if [ -n "$other" ]; then
    echo "NOT MERGED $b: changes files outside stories/ and films/ (pull request needed): $(echo $other)"
    git reset -q --hard "$before"
    continue
  fi
  if ! python3 tools/filmtool.py check >/dev/null; then
    echo "NOT MERGED $b: filmtool check failed"
    git reset -q --hard "$before"
    continue
  fi
  if [ -n "$(git status --porcelain -- films-index.json)" ]; then
    git add films-index.json && git commit -q --amend --no-edit
  fi
  echo "merged $b"
done
exit 0
