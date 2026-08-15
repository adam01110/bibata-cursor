#!/usr/bin/env bash

set -euo pipefail

resolve_did() {
  curl -fsSG "https://public.api.bsky.app/xrpc/com.atproto.identity.resolveHandle" \
    --data-urlencode "handle=$ATP_IDENTIFIER" | jq -er .did
}

resolve_pds() {
  local did=$1

  case "$did" in
  did:plc:*)
    curl -fsS "https://plc.directory/$did" | jq -er \
      '[.service[] | select(.type == "AtprotoPersonalDataServer")][0].serviceEndpoint'
    ;;
  *)
    echo "Unsupported DID method: $did" >&2
    return 1
    ;;
  esac
}

publish_artifact() {
  local artifact_path=$1
  local artifact_name blob record

  artifact_name=$(basename "$artifact_path")
  blob=$(curl -fsS -X POST "$pds/xrpc/com.atproto.repo.uploadBlob" \
    -H "Authorization: Bearer $jwt" \
    -H "Content-Type: application/octet-stream" \
    --data-binary "@$artifact_path")
  record=$(jq -n \
    --arg did "$did" \
    --arg tag "$tag_bytes" \
    --arg name "$artifact_name" \
    --arg repo "$TANGLED_REPO_URL" \
    --arg created "$(date -Iseconds)" \
    --argjson blob "$(jq .blob <<<"$blob")" \
    '{repo: $did, collection: "sh.tangled.repo.artifact", validate: false, record: {"$type": "sh.tangled.repo.artifact", tag: {"$bytes": $tag}, name: $name, repo: $repo, artifact: $blob, createdAt: $created}}')
  curl -fsS -X POST "$pds/xrpc/com.atproto.repo.createRecord" \
    -H "Authorization: Bearer $jwt" \
    -H "Content-Type: application/json" \
    -d "$record"
}

if [[ $TANGLED_PIPELINE_KIND == "manual" ]]; then
  echo "Manual pipelines build and package artifacts without publishing them."
  exit 0
fi

resolved_did=$(resolve_did)
pds=$(resolve_pds "$resolved_did")
pds=${pds%/}

session=$(curl -fsS -X POST "$pds/xrpc/com.atproto.server.createSession" \
  -H "Content-Type: application/json" \
  -d "$(jq -n \
    --arg identifier "$ATP_IDENTIFIER" \
    --arg password "$ATP_APP_PASSWORD" \
    '{identifier: $identifier, password: $password}')")
jwt=$(jq -r .accessJwt <<<"$session")
did=$(jq -r .did <<<"$session")
[[ $did == "$resolved_did" ]]

tag_hash=$(git rev-parse "$TANGLED_REF_NAME^{tag}")
tag_bytes=$(printf '%s' "$tag_hash" | xxd -r -p | base64 | tr -d '=')

for artifact_path in dist/*.zip; do
  publish_artifact "$artifact_path"
done
