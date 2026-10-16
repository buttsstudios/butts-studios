#!/usr/bin/env bash
# novels.buttsstudios.com updates list -> Resend audience. STAGED 2026-10-16, nothing run.
# The form posts to /api/subscribe (publication/the-signal/api/subscribe.js). Until the Vercel project has
# RESEND_API_KEY + RESEND_AUDIENCE_ID it answers 503 and the page says "not open yet"; nothing is stored.
#
# Needs: RESEND_API_KEY in ~/.config/ahl/SETUP_DROP.env (setup sheet Resend row); the Butts Studios Vercel token
# (setup row vercel-butts-deploy) as VERCEL_TOKEN for step 2. No sending domain is needed to add contacts.
#
# Usage: ./novels_resend_setup.sh            dry run: says whether the key exists, lists audiences by name
#        CONFIRM=GO ./novels_resend_setup.sh create the audience (if missing) + set the two Vercel env vars
# Values are never printed.
set -euo pipefail
NAME="The Signal updates"
KEY=$(awk -F= '/^RESEND_API_KEY=/{sub(/^RESEND_API_KEY=/,""); print}' ~/.config/ahl/SETUP_DROP.env | tail -1)
[[ -n "$KEY" ]] || { echo "WAIT: RESEND_API_KEY is empty in SETUP_DROP.env (setup sheet row)"; exit 1; }
API=https://api.resend.com
H=(-H "Authorization: Bearer $KEY" -H "Content-Type: application/json")

list=$(curl -s "${API}/audiences" "${H[@]}")
AID=$(python3 -c 'import sys,json;d=json.load(sys.stdin).get("data") or [];print(next((a["id"] for a in d if a.get("name")==sys.argv[1]),""))' "$NAME" <<<"$list")
echo "audience '$NAME': ${AID:+exists}${AID:-missing}"
[[ "${CONFIRM:-}" == GO ]] || { echo "dry run; CONFIRM=GO to create + set Vercel env"; exit 0; }

if [[ -z "$AID" ]]; then
  AID=$(curl -s -X POST "${API}/audiences" "${H[@]}" --data "{\"name\":\"$NAME\"}" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("id",""))')
  [[ -n "$AID" ]] || { echo "STOP: audience create failed"; exit 1; }
  echo "audience created"
fi

: "${VERCEL_TOKEN:?set VERCEL_TOKEN (Butts Studios Vercel)}"
cd ~/buttsstudios/publication/the-signal
for v in RESEND_API_KEY RESEND_AUDIENCE_ID; do
  val=$([[ $v == RESEND_API_KEY ]] && printf %s "$KEY" || printf %s "$AID")
  vercel env rm "$v" production --yes --token "$VERCEL_TOKEN" >/dev/null 2>&1 || true
  printf %s "$val" | vercel env add "$v" production --token "$VERCEL_TOKEN" >/dev/null && echo "env $v set"
done
echo "redeploy novels (env applies on the next deploy), then: curl -s https://novels.buttsstudios.com/api/subscribe  -> {\"open\":true}"
