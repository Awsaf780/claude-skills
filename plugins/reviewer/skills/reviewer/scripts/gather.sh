#!/usr/bin/env bash
# Collects everything a PR review needs into one folder, so the review reads files
# instead of re-running gh calls. Read-only on GitHub and on the user's working tree.
#
#   gather.sh <pr-url | owner/repo#N | N>   (a bare N uses the repo of the current directory)
#   gather.sh --cleanup <review-dir>          removes the head worktree made by an earlier run
#
# Prints the review folder path on the last line.
set -euo pipefail
export LC_ALL=C

if [[ "${1:-}" == "--cleanup" ]]; then
  dir="$2"
  if [[ -f "$dir/clone-path" && -d "$dir/head" ]]; then
    git -C "$(cat "$dir/clone-path")" worktree remove --force "$dir/head" && echo "removed $dir/head"
  fi
  exit 0
fi

ref="${1:?usage: gather.sh <pr-url | owner/repo#N | N>}"
if [[ "$ref" =~ github\.com/([^/]+)/([^/]+)/pull/([0-9]+) ]]; then
  repo="${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"; n="${BASH_REMATCH[3]}"
elif [[ "$ref" =~ ^([^/#]+/[^/#]+)#([0-9]+)$ ]]; then
  repo="${BASH_REMATCH[1]}"; n="${BASH_REMATCH[2]}"
elif [[ "$ref" =~ ^#?([0-9]+)$ ]]; then
  n="${BASH_REMATCH[1]}"; repo="$(gh repo view --json nameWithOwner -q .nameWithOwner)"
else
  echo "can't parse PR reference: $ref" >&2; exit 1
fi

dir="$HOME/.claude/reviews/${repo/\//__}/pr-$n"
mkdir -p "$dir"
cd "$dir"

gh pr view "$n" -R "$repo" --json number,title,author,state,isDraft,baseRefName,headRefName,headRefOid,additions,deletions,changedFiles,body,url > pr.json
head_sha=$(jq -r .headRefOid pr.json)
base=$(jq -r .baseRefName pr.json)

# All feedback lives in three places: review bodies, inline threads and the conversation.
{
  echo "# Review bodies"
  gh api --paginate "repos/$repo/pulls/$n/reviews" \
    --jq '.[] | select(.body != "") | "\n## \(.user.login) [\(.state)] \(.submitted_at) commit=\(.commit_id[0:9])\n\(.body)"'
  echo; echo "# Inline threads (reply_to links a reply to its parent)"
  gh api --paginate "repos/$repo/pulls/$n/comments" \
    --jq '.[] | "\n## id=\(.id) reply_to=\(.in_reply_to_id // "-") \(.user.login) \(.path):\(.line // .original_line) commit=\(.commit_id[0:9]) outdated=\(.line == null)\n\(.body)"'
  echo; echo "# Conversation"
  gh api --paginate "repos/$repo/issues/$n/comments" \
    --jq '.[] | select(.user.type != "Bot") | "\n## \(.user.login) \(.created_at)\n\(.body)"'
} > comments.md

gh pr diff "$n" -R "$repo" > diff.patch
gh pr view "$n" -R "$repo" --json files --jq '.files[] | "\(.additions)+ \(.deletions)- \(.path)"' > files.txt
gh pr checks "$n" -R "$repo" > checks.txt 2>&1 || true

# Tickets the PR links or names, in this repo or another.
{
  gh api graphql -f query="{repository(owner:\"${repo%/*}\",name:\"${repo#*/}\"){pullRequest(number:$n){closingIssuesReferences(first:10){nodes{number repository{nameWithOwner}}}}}}" \
    --jq '.data.repository.pullRequest.closingIssuesReferences.nodes[] | "\(.repository.nameWithOwner)#\(.number)"' 2>/dev/null || true
  jq -r .body pr.json | grep -oE '([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)?#[0-9]+|github\.com/[^/ ]+/[^/ ]+/issues/[0-9]+' || true
} | sed -E 's#github\.com/([^/]+)/([^/]+)/issues/#\1/\2\##; s#^\##'"$repo"'\##' | sort -u > linked.txt
: > tickets.md
while read -r t; do
  r="${t%#*}"; i="${t#*#}"
  if [[ "$r" == "$repo" && "$i" == "$n" ]]; then continue; fi
  # The comments matter as much as the body: owners often change a criterion in a comment.
  gh issue view "$i" -R "$r" --json title,state,body,url,comments \
    --jq '"\n# \(.url) [\(.state)] \(.title)\n\(.body)" + (if (.comments | length) > 0
      then "\n\n## Comments on this ticket\n" + ([.comments[] | "\n### \(.author.login) \(.createdAt)\n\(.body)"] | join("\n"))
      else "" end)' >> tickets.md 2>/dev/null || true
done < linked.txt

# Open PRs that touch the same files can conflict with, or depend on, this one.
gh pr list -R "$repo" --state open --limit 50 --json number,title,author,files \
  --jq ".[] | select(.number != $n) | {number, title, author: .author.login, files: [.files[].path]}" > open-prs.jsonl
cut -d' ' -f3- files.txt | sort -u > .paths
: > overlapping-prs.txt
while read -r pr; do
  hits=$(jq -r '.files[]' <<<"$pr" | sort -u | comm -12 - .paths | head -5 | paste -sd, -)
  if [[ -n "$hits" ]]; then
    jq -r --arg h "$hits" '"#\(.number) \(.title) (\(.author)): \($h)"' <<<"$pr" >> overlapping-prs.txt
  fi
done < open-prs.jsonl
rm -f .paths

# A local clone lets the review read whole files at the PR head and see what the base
# gained since the branch was cut. The worktree sits here, outside the clone.
clone=""
read -ra roots <<<"${REVIEWER_CLONE_DIRS:-$HOME/Workspace $HOME/code $HOME/src $HOME/projects}"
candidates=("$PWD" "$OLDPWD")
for r in "${roots[@]}"; do candidates+=("$r"/*); done
for c in "${candidates[@]}"; do
  [[ -d "$c/.git" ]] || continue
  url=$(git -C "$c" remote get-url origin 2>/dev/null || true)
  if [[ "$url" =~ [:/]${repo}(\.git)?$ ]]; then clone="$c"; break; fi
done
if [[ -n "$clone" ]]; then
  echo "$clone" > clone-path
  git -C "$clone" fetch -q origin "$base" "pull/$n/head"
  if [[ ! -d head ]]; then
    git -C "$clone" worktree add -q --detach "$dir/head" "$head_sha"
  else
    git -C "$dir/head" checkout -q --detach "$head_sha"
  fi
  mb=$(git -C "$clone" merge-base "origin/$base" "$head_sha")
  # A dry-run merge: the first line is the tree the merge would produce (conflict markers
  # included), then the conflicting files. Nothing in the clone changes.
  merged=$(git -C "$clone" merge-tree --write-tree --name-only "origin/$base" "$head_sha" 2>/dev/null || true)
  head -1 <<<"$merged" > merge-tree.txt
  {
    echo "# Commits on $base since this branch was cut ($(git -C "$clone" rev-list --count "$mb..origin/$base") total)"
    git -C "$clone" log --oneline "$mb..origin/$base" | head -40
    echo; echo "# Of those, touching files this PR changes"
    git -C "$clone" log --oneline "$mb..origin/$base" -- $(cut -d' ' -f3- files.txt) | head -40
    echo; echo "# Files that would conflict on merge"
    tail -n +2 <<<"$merged" | sed '/^$/,$d'
    echo; echo "# Read a file as it would be after the merge"
    echo "git -C $clone show $(cat merge-tree.txt):<path>"
  } > base-drift.md
else
  echo "no local clone of $repo found; read files with: gh api repos/$repo/contents/<path>?ref=$head_sha" > base-drift.md
fi

echo "repo=$repo pr=$n head=${head_sha:0:9} base=$base clone=${clone:-none}"
wc -l comments.md diff.patch files.txt tickets.md overlapping-prs.txt | sed '$d'
echo "$dir"
