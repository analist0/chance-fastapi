#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")/.."

ENV_FILE="${ENV_FILE:-.env}"
KEY_NAME="${KEY_NAME:-STITCH_API_KEY}"

printf "Enter Google Stitch API key: "
stty -echo
IFS= read -r api_key
stty echo
printf "\n"

if [ -z "$api_key" ]; then
  printf "FAILURE: API key cannot be empty.\n" >&2
  exit 1
fi

case "$api_key" in
  *[!A-Za-z0-9._-]*)
    printf "FAILURE: API key contains unsupported characters.\n" >&2
    exit 1
    ;;
esac

touch "$ENV_FILE"
chmod 600 "$ENV_FILE"

tmp_file="$(mktemp)"
if grep -q "^${KEY_NAME}=" "$ENV_FILE"; then
  sed "s#^${KEY_NAME}=.*#${KEY_NAME}=${api_key}#" "$ENV_FILE" > "$tmp_file"
else
  cat "$ENV_FILE" > "$tmp_file"
  if [ -s "$ENV_FILE" ]; then
    printf "\n" >> "$tmp_file"
  fi
  printf "%s=%s\n" "$KEY_NAME" "$api_key" >> "$tmp_file"
fi

cat "$tmp_file" > "$ENV_FILE"
rm -f "$tmp_file"
chmod 600 "$ENV_FILE"

printf "SUCCESS: saved %s in %s\n" "$KEY_NAME" "$ENV_FILE"
printf "The key value was not printed. Keep %s out of Git.\n" "$ENV_FILE"
