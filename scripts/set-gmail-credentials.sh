#!/usr/bin/env bash
# set-gmail-credentials.sh — write GMAIL_SEND_ADDRESS + GMAIL_APP_PASSWORD
# to ~/.config/research-bot/env without clobbering anything else there.
#
# Usage:
#   scripts/set-gmail-credentials.sh <email> <app-password>
#
# Example:
#   # The leading space keeps this out of shell history when HISTCONTROL=ignorespace
#   # (the default on macOS zsh). Always prefix secret-bearing commands with a space.
#    scripts/set-gmail-credentials.sh you@gmail.com "xxxx xxxx xxxx xxxx"
#
# The app password can be pasted with or without spaces — Google accepts both
# and the script strips whitespace from the password before writing.
#
# Idempotent: re-running replaces the two GMAIL_* lines; other keys (e.g.
# ANTHROPIC_API_KEY) and comments are preserved exactly.

set -euo pipefail

if [[ $# -lt 2 ]]; then
    cat <<EOF >&2
usage: $0 <email> <app-password>

Example (note the leading space so it stays out of shell history):
   $0 you@gmail.com "xxxx xxxx xxxx xxxx"

To get an app password:
  1. Enable 2-Step Verification on your Google account.
  2. Visit https://myaccount.google.com/apppasswords
  3. App: "Mail" → Device: "Other (Custom name)" → "research-bot"
  4. Copy the 16-character password shown once.
EOF
    exit 2
fi

EMAIL="$1"
RAW_PASSWORD="$2"

# Strip whitespace from password (Google displays as "xxxx xxxx xxxx xxxx")
PASSWORD="${RAW_PASSWORD// /}"

if [[ -z "$PASSWORD" ]]; then
    echo "ERROR: password is empty after whitespace strip" >&2
    exit 2
fi

if [[ "$EMAIL" != *"@"* ]]; then
    echo "ERROR: '$EMAIL' doesn't look like an email address" >&2
    exit 2
fi

ENV_DIR="$HOME/.config/research-bot"
ENV_FILE="$ENV_DIR/env"

mkdir -p "$ENV_DIR"
chmod 700 "$ENV_DIR"
touch "$ENV_FILE"
chmod 600 "$ENV_FILE"

# Use Python to update/append — avoids sed escaping pitfalls with special chars.
python3 - "$EMAIL" "$PASSWORD" "$ENV_FILE" <<'PYEOF'
import sys
from pathlib import Path

email, password, path = sys.argv[1], sys.argv[2], Path(sys.argv[3])

existing = path.read_text().splitlines() if path.exists() else []
keys_to_set = {
    "GMAIL_SEND_ADDRESS": email,
    "GMAIL_APP_PASSWORD": password,
}

seen = set()
new_lines = []
for line in existing:
    stripped = line.lstrip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        new_lines.append(line)
        continue
    key = stripped.split("=", 1)[0].strip()
    if key in keys_to_set:
        new_lines.append(f"{key}={keys_to_set[key]}")
        seen.add(key)
    else:
        new_lines.append(line)

for key, val in keys_to_set.items():
    if key not in seen:
        new_lines.append(f"{key}={val}")

path.write_text("\n".join(new_lines).rstrip() + "\n")
print(f"OK: wrote GMAIL_SEND_ADDRESS + GMAIL_APP_PASSWORD to {path}")
PYEOF

PERMS=$(ls -l "$ENV_FILE" | awk '{print $1}')
echo "  Permissions: $PERMS (should be -rw-------)"
echo "  Test with:"
echo "    python3 -c 'import smtplib, os; \\"
echo "      from pathlib import Path; \\"
echo "      env={l.split(\"=\",1)[0]:l.split(\"=\",1)[1] for l in Path(\"$ENV_FILE\").read_text().splitlines() if l and not l.startswith(\"#\") and \"=\" in l}; \\"
echo "      s=smtplib.SMTP_SSL(\"smtp.gmail.com\",465); \\"
echo "      s.login(env[\"GMAIL_SEND_ADDRESS\"], env[\"GMAIL_APP_PASSWORD\"]); \\"
echo "      print(\"SMTP login OK\"); s.quit()'"
