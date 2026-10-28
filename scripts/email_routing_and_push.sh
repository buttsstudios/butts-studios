#!/usr/bin/env bash
# R-buttsstudios-dead-domain-1 · staged by the STUDIOS lane 2026-10-12. Run by the operator.
#
# 1) Cloudflare Email Routing on buttsstudios.com: catch-all -> buttsstudios@gmail.com
#    (covers hello@, team@ and the film@, animation@, clients@, support@ addresses on the live pages).
#    Needs CF_API_TOKEN for the Cloudflare account that owns the zone (NS uma/weston.ns.cloudflare.com), with:
#      Zone: Email Routing Rules Edit · Zone: DNS Edit · Account: Email Routing Addresses Edit
# 2) Push the five live-page repos (address fix already committed locally). Needs a GitHub login with push
#    access to the buttsstudios org (the token embedded in the old remotes is expired).
#
# Usage: CF_API_TOKEN=... ./email_routing_and_push.sh          (dry run: prints what it would do)
#        CF_API_TOKEN=... ./email_routing_and_push.sh --go
set -euo pipefail
GO=${1:-}
DEST="buttsstudios@gmail.com"
ZONE_NAME="buttsstudios.com"
API="https://api.cloudflare.com/client/v4"
: "${CF_API_TOKEN:?set CF_API_TOKEN}"
H=(-H "Authorization: Bearer ${CF_API_TOKEN}" -H "Content-Type: application/json")

zone_json=$(curl -s "${API}/zones?name=${ZONE_NAME}" "${H[@]}")
ZONE_ID=$(python3 -c 'import sys,json;r=json.load(sys.stdin)["result"];print(r[0]["id"] if r else "")' <<<"$zone_json")
ACCOUNT_ID=$(python3 -c 'import sys,json;r=json.load(sys.stdin)["result"];print(r[0]["account"]["id"] if r else "")' <<<"$zone_json")
[ -n "$ZONE_ID" ] || { echo "zone ${ZONE_NAME} not visible to this token"; exit 1; }
echo "zone ${ZONE_NAME} found"

run() { if [ "$GO" = "--go" ]; then "$@"; echo; else echo "DRY: $*" | sed 's/Bearer [^ ]*/Bearer <token>/'; fi; }

# a) turn on Email Routing (Cloudflare adds the MX + SPF records)
run curl -s -X POST "${API}/zones/${ZONE_ID}/email/routing/dns" "${H[@]}"
# b) destination address: Cloudflare emails ${DEST} a verification link (the Principal clicks it)
run curl -s -X POST "${API}/accounts/${ACCOUNT_ID}/email/routing/addresses" "${H[@]}" --data "{\"email\":\"${DEST}\"}"
# c) catch-all rule -> forward to ${DEST} (it starts delivering once the address is verified)
run curl -s -X PUT "${API}/zones/${ZONE_ID}/email/routing/rules/catch_all" "${H[@]}" \
  --data "{\"enabled\":true,\"name\":\"catch-all to buttsstudios@gmail.com\",\"matchers\":[{\"type\":\"all\"}],\"actions\":[{\"type\":\"forward\",\"value\":[\"${DEST}\"]}]}"

# verify
if [ "$GO" = "--go" ]; then
  echo "MX now:"; dig +short MX "${ZONE_NAME}"
fi

# 2) push the live-page fixes (Vercel redeploys from GitHub)
ROOT="$HOME/buttsstudios"
for d in production/film production/animation publication/the-signal games/glb apps/butts-clients-next games/portal; do  # games/portal: favicon fix R-buttsstudios-games-icons-1 (92826ff) + no-"free" copy R-buttsstudios-2 (b28f2cc)
  run git -C "${ROOT}/${d}" push origin main
done
if [ "$GO" = "--go" ]; then
  sleep 90
  for h in film animation clients; do
    printf "%s: " "$h"; curl -s "https://${h}.buttsstudios.com" | grep -o '[a-z]*@butts[-a-z]*studios\.com' | sort -u | tr '\n' ' '; echo
  done
  printf "games favicon: "; curl -s -o /dev/null -w '%{http_code}\n' https://games.buttsstudios.com/favicon.ico
  printf "games 'free' count (want 0): "; curl -s https://games.buttsstudios.com/ | grep -ci free || true
fi
