#!/usr/bin/env bash
# Post-deploy check for the URL map: canonical pages 200; retired URLs 404 with no forwarding (Principal 2026-10-28:
# "no forwarding except for the domains we particularly setup for the purpose of forwarding").
# Read-only. Usage: bash scripts/verify_url_map_live.sh [--hosts]   (--hosts after ~/go-remove-studios-subdomains.sh ran)
base=https://buttsstudios.com; fail=0
chk() { local got; got=$(curl -s -o /dev/null -w '%{http_code} %{redirect_url}' --max-time 20 "$1"); [[ "$got" == "$2"* ]] && echo "ok   $1 -> $got" || { echo "FAIL $1 -> $got (want $2)"; fail=1; }; }
for p in / /games /games/glowgrid /games/cards /games/sliding-numbers /titles /titles/talon /titles/the-little-things /titles/us-against-the-world /titles/runwae-and-glb /channels /books /video /work /portfolio /portfolio/chief /how-we-work /partnerships /shop /terms /privacy /refunds /sitemap.xml /robots.txt; do chk "$base$p" "200"; done
for p in /games.html /slate.html /slate /titles/the-channels.html /titles/the-channels /titles/talon.html /books.html /portfolio/chief.html /the-signal /refund; do chk "$base$p" "404"; done
if [ "$1" = "--hosts" ]; then
  for h in glb cards puzzle games portal store novels film animation clients; do
    if host "$h.buttsstudios.com" >/dev/null 2>&1; then echo "FAIL $h.buttsstudios.com still resolves"; fail=1; else echo "ok   $h.buttsstudios.com removed (no DNS)"; fi
  done
fi
exit $fail
