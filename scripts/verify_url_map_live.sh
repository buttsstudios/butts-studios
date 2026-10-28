#!/usr/bin/env bash
# Post-deploy check for the URL map: canonical pages 200, legacy .html paths 301 to them, old game hosts 301 to /games/*.
# Read-only. Usage: bash scripts/verify_url_map_live.sh [--hosts]   (--hosts only after the subdomains moved projects)
base=https://buttsstudios.com; fail=0
chk() { local got; got=$(curl -s -o /dev/null -w '%{http_code} %{redirect_url}' --max-time 20 "$1"); [[ "$got" == "$2"* ]] && echo "ok   $1 -> $got" || { echo "FAIL $1 -> $got (want $2)"; fail=1; }; }
for p in / /games /games/glowgrid /games/cards /games/sliding-numbers /titles /titles/talon /titles/the-little-things /titles/us-against-the-world /titles/runwae-and-glb /channels /books /video /work /portfolio /portfolio/chief /how-we-work /partnerships /shop /terms /privacy /refunds /sitemap.xml; do chk "$base$p" "200"; done
chk $base/games.html "301 $base/games"; chk $base/slate.html "301 $base/titles"; chk $base/titles/the-channels.html "301 $base/channels"
chk $base/titles/talon.html "301 $base/titles/talon"; chk $base/books.html "301 $base/books"; chk $base/portfolio/chief.html "301 $base/portfolio/chief"
if [ "$1" = "--hosts" ]; then
  chk https://glb.buttsstudios.com/ "301 $base/games/glowgrid"; chk https://cards.buttsstudios.com/ "301 $base/games/cards"
  chk https://puzzle.buttsstudios.com/ "301 $base/games/sliding-numbers"; chk https://games.buttsstudios.com/ "301 $base/games"
  chk https://store.buttsstudios.com/ "301 $base/shop"; chk "https://glb.buttsstudios.com/?session_id=cs_test_x" "301 $base/games/glowgrid?session_id=cs_test_x"
fi
exit $fail
