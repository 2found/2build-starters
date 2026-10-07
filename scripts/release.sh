#!/usr/bin/env bash
# Called only after the checked-out commit passes generated-project verification.
set -euo pipefail

version="$(jq -er '.version | strings | select(test("^(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)$"))' catalog.json)"
tag="v$version"
sha="$(git rev-parse HEAD)"
if [ "$sha" != "${GITHUB_SHA:?}" ]; then
  echo 'Refusing to release a commit different from the verified workflow commit.' >&2
  exit 1
fi
if [ "${GITHUB_REF:?}" != refs/heads/main ] && [ "$GITHUB_REF" != "refs/tags/$tag" ]; then
  echo "Release ref $GITHUB_REF must be main or refs/tags/$tag." >&2
  exit 1
fi

scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT
if gh release view "$tag" --json isDraft,isPrerelease >"$scratch/release.json" 2>"$scratch/error"; then
  jq -e '(.isDraft == false) and (.isPrerelease == false)' "$scratch/release.json" >/dev/null
  echo "$tag is already published; retaining its immutable contents."
  exit 0
else
  # A service/auth failure is not evidence that this version is unpublished.
  case "$(cat "$scratch/error")" in
    *"release not found"*) ;;
    *) cat "$scratch/error" >&2; exit 1 ;;
  esac
fi

if git show-ref --verify --quiet "refs/tags/$tag"; then
  if [ "$(git rev-list -n 1 "$tag")" != "$sha" ]; then
    echo "$tag points at another commit; refusing to publish unverified contents." >&2
    exit 1
  fi
else
  git config user.name 'github-actions[bot]'
  git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
  git tag -a "$tag" -m "$tag"
fi
# Creating the tag here does not need another workflow: this job already waited
# for integration, and GITHUB_TOKEN pushes do not trigger tag workflows.
git push origin "refs/tags/$tag"
gh release create "$tag" --verify-tag --title "$tag" --generate-notes
