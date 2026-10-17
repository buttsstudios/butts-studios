#!/usr/bin/env bash
# Butts Studios games: premium-bypass fix + no-.99 pricing. STAGED 2026-10-15, nothing deployed.
#
# Modes:
#   check          read-only: branches present, placeholders, bypass strings, live state
#   fix            GO-gated: push the PINNED SHAs (see PIN below) of fix/verify-purchase-2026-10-15 (glb, cards,
#                  puzzle) and fix/one-time-label-2026-10-15 (portal hub) to origin/main; STOP if a tip != pin
#   price          GO-gated: fill the new Payment Link URLs, then push price/no-99-2026-10-15
#   verify         read-only curls after a deploy
#
# Before `fix` (Principal / Stripe dashboard, test mode first):
#   1. A Stripe RESTRICTED key with Checkout Sessions: Read only, on the account that owns the links.
#      Vercel env on projects glb-game, butts-cards, butts-puzzle:
#        STRIPE_READ_KEY, PREMIUM_PAYMENT_LINKS (comma list of plink_ ids that unlock that game;
#        cards: hub link ...Re01 AND in-game ...Re08; puzzle: hub ...Re02 AND in-game ...Re07; glb: hub ...Re03)
#   2. Each of those Payment Links: After payment -> redirect to
#        https://<game host>/?session_id={CHECKOUT_SESSION_ID}
#      (Without this, buyers land with no session_id and nothing unlocks.)
# Before `price`: new one-time Payment Links at $5 (GLB) and $3 (Cards, Puzzle), same redirect rule,
#   exported as NEW_PAYMENT_LINK_GLB_5, NEW_PAYMENT_LINK_CARDS_3, NEW_PAYMENT_LINK_PUZZLE_3, and their
#   plink_ ids added to PREMIUM_PAYMENT_LINKS. Then deactivate the old .99 links.
# 2026-10-17 P0 sprint: branches rebased onto origin tips after the XE-4/XE-7 legal+copy deploy
#   (glb 1f68209, portal f65f351); portal's old 'free' commit b28f2cc dropped as already live.
# Rollback: fix forward. A revert/promote needs the Principal (2026-10-13 rule): ROLLBACK_OK=principal.
set -euo pipefail
B=~/buttsstudios
REPOS_FIX=("games/glb:fix/verify-purchase-2026-10-15" "apps/butts-cards-next:fix/verify-purchase-2026-10-15" "apps/butts-puzzle-next:fix/verify-purchase-2026-10-15" "games/portal:fix/one-time-label-2026-10-15")
# SHA pins (P0 rework 2026-10-17, XE-1 GO gap): `fix` pushes these exact commits, never the branch tip. Each branch tip
# must equal its pin and origin/main..pin must be exactly the listed commits, or STOP (re-review, re-pin).
#   glb    1cc5a1a = the verified fix; f854965 (contact domain butts-studios.com -> buttsstudios.com) rides under it
#   cards  4a70aa6, puzzle 421c7ff = the verified fixes
#   portal 61ce898 hub "one-time" copy; 595d394 (favicon/apple-touch-icon files) rides under it
# (bash 3.2 on macOS: no associative arrays, so pins are a lookup function)
pin_of() { case "$1" in   # <full SHA> <exact origin/main..PIN commit list, oldest first>
  games/glb)              echo "1cc5a1ad1bbf5ababa5aa20ef284d9651eaa16ff f85496529c7f933a64d86e23cc4aa857958cb030 1cc5a1ad1bbf5ababa5aa20ef284d9651eaa16ff";;
  apps/butts-cards-next)  echo "4a70aa6f62b42e849879142595f32122123a6503 4a70aa6f62b42e849879142595f32122123a6503";;
  apps/butts-puzzle-next) echo "421c7ff7b032e5f22e50b93ef0e577ceffa5a1fa 421c7ff7b032e5f22e50b93ef0e577ceffa5a1fa";;
  games/portal)           echo "61ce89808082fbe0917dffd06e8f941b86012b08 595d39470552aae3e18d85c0938762286b20a1aa 61ce89808082fbe0917dffd06e8f941b86012b08";;
  *) echo "";; esac; }
REPOS_PRICE=("games/glb" "apps/butts-cards-next" "apps/butts-puzzle-next" "games/portal")
HOSTS=(glb cards puzzle games)

# DRY=1 <fix|price>: full preflight (ff check against origin tip + `git push --dry-run`), no push, no prompt.
gate() { [[ "${DRY:-0}" == 1 ]] && { echo "DRY: would $1"; return; }; [[ "${CONFIRM:-}" == "GO" ]] && return; read -r -p "Type GO to $1: " a; [[ "$a" == "GO" ]] || { echo "aborted"; exit 1; }; }

check() {
  for e in "${REPOS_FIX[@]}"; do r=${e%%:*}; br=${e##*:}
    git -C "$B/$r" rev-parse -q --verify "$br" >/dev/null && echo "ok   $r $br $(git -C "$B/$r" log --oneline -1 "$br")" || echo "MISS $r $br"
    if git -C "$B/$r" grep -n "get('premium')\|'/?premium=true'" "$br" -- ':!index.html' 2>/dev/null | grep -q .; then echo "FAIL bypass string still in $r"; fi
  done
  # Next apps carry an unserved legacy root index.html; glb's index.html IS served:
  git -C "$B/games/glb" grep -q "premium=true" fix/verify-purchase-2026-10-15 -- index.html && echo "FAIL glb bypass" || echo "ok   glb served page clean"
  for r in "${REPOS_PRICE[@]}"; do
    n=$(git -C "$B/$r" grep -c "__NEW_PAYMENT_LINK_" price/no-99-2026-10-15 2>/dev/null | awk -F: '{s+=$NF} END{print s+0}')
    echo "price $r placeholders=$n"
  done
  for h in "${HOSTS[@]}"; do printf "live %-7s %s\n" "$h" "$(curl -s -o /dev/null -w '%{http_code}' "https://$h.buttsstudios.com/")"; done
}

push_branch() { local r=$1 br=$2
  git -C "$B/$r" fetch -q origin
  git -C "$B/$r" merge-base --is-ancestor origin/main "$br" || { echo "STOP $r: $br does not fast-forward origin/main; rebase first"; exit 1; }
  if [[ "${DRY:-0}" == 1 ]]; then git -C "$B/$r" push --dry-run origin "$br:main" 2>&1 | tail -1 | sed "s#^#DRY $r: #"; return; fi
  git -C "$B/$r" push origin "$br:main"
}

# fix mode: push the PINNED SHA (never the moving branch tip). STOP unless tip == pin and the range is exactly as reviewed.
push_pin() { local r=$1 br=$2 spec pin tip got want c
  spec=$(pin_of "$r"); pin=${spec%% *}; want=${spec#* }
  [[ ${#pin} -eq 40 ]] || { echo "STOP $r: no full-SHA pin"; exit 1; }
  git -C "$B/$r" fetch -q origin
  git -C "$B/$r" cat-file -e "$pin^{commit}" 2>/dev/null || { echo "STOP $r: pin ${pin:0:7} not found"; exit 1; }
  tip=$(git -C "$B/$r" rev-parse -q --verify "refs/heads/$br" || true)
  [[ "$tip" == "$pin" ]] || { echo "STOP $r: $br tip ${tip:0:7} != pin ${pin:0:7} (branch moved; re-review and re-pin)"; exit 1; }
  git -C "$B/$r" merge-base --is-ancestor origin/main "$pin" || { echo "STOP $r: pin ${pin:0:7} does not fast-forward origin/main; rebase + re-pin"; exit 1; }
  got=$(git -C "$B/$r" rev-list --reverse origin/main.."$pin" | tr '\n' ' ' | sed 's/ $//')
  set -- $got
  [[ $# -eq $(wc -w <<<"$want") ]] || { echo "STOP $r: origin/main..pin = $(git -C "$B/$r" log --oneline --reverse origin/main.."$pin" | cut -c1-8 | tr '\n' ' '), want $want"; exit 1; }
  local i=1; for c in $want; do [[ "${!i}" == "$c" ]] || { echo "STOP $r: commit $i is ${!i:0:8}, want $c"; exit 1; }; i=$((i+1)); done
  echo "ok   $r: $br == pin ${pin:0:7}; origin/main($(git -C "$B/$r" rev-parse --short origin/main))..pin = $(for c in $want; do printf "%s " "${c:0:7}"; done)"
  if [[ "${DRY:-0}" == 1 ]]; then git -C "$B/$r" push --dry-run origin "$pin:refs/heads/main" 2>&1 | tail -1 | sed "s#^#DRY $r: #"; return; fi
  git -C "$B/$r" push origin "$pin:refs/heads/main"
  [[ "$(git -C "$B/$r" ls-remote origin refs/heads/main | cut -f1)" == "$pin" ]] || { echo "STOP $r: origin/main != pin after push"; exit 1; }
}

fix() {
  gate "push the premium-bypass fix to glb, cards, puzzle and the hub"
  for e in "${REPOS_FIX[@]}"; do push_pin "${e%%:*}" "${e##*:}"; done
  [[ "${DRY:-0}" == 1 ]] && echo "DRY PASS (nothing pushed)" || echo "pushed; run: $0 verify"
}

price() {
  for v in NEW_PAYMENT_LINK_GLB_5 NEW_PAYMENT_LINK_CARDS_3 NEW_PAYMENT_LINK_PUZZLE_3; do
    [[ "${!v:-}" =~ ^https://buy\.stripe\.com/[A-Za-z0-9]+$ ]] || { echo "STOP: $v unset or not a buy.stripe.com URL"; exit 1; }
  done
  gate "fill the new links and push the \$5/\$3 pricing"
  for r in "${REPOS_PRICE[@]}"; do
    git -C "$B/$r" checkout -q price/no-99-2026-10-15
    for f in $(git -C "$B/$r" grep -l "__NEW_PAYMENT_LINK_" || true); do
      sed -i '' -e "s#__NEW_PAYMENT_LINK_GLB_5__#$NEW_PAYMENT_LINK_GLB_5#g" \
                -e "s#__NEW_PAYMENT_LINK_CARDS_3__#$NEW_PAYMENT_LINK_CARDS_3#g" \
                -e "s#__NEW_PAYMENT_LINK_PUZZLE_3__#$NEW_PAYMENT_LINK_PUZZLE_3#g" "$B/$r/$f"
    done
    if git -C "$B/$r" grep -q "__NEW_PAYMENT_LINK_"; then echo "STOP: placeholder left in $r"; exit 1; fi
    git -C "$B/$r" commit -qam "price: fill new no-.99 Payment Links" || true
    push_branch "$r" price/no-99-2026-10-15
  done
}

verify() {
  for h in glb cards puzzle; do
    c=$(curl -s -o /dev/null -w '%{http_code}' "https://$h.buttsstudios.com/api/verify-purchase?session_id=bad")
    echo "$h verify-purchase bad id -> $c (want 400)"
    curl -s "https://$h.buttsstudios.com/?premium=true" | grep -q "premium=true" && echo "FAIL $h still references premium=true" || echo "ok   $h page has no premium=true"
  done
  curl -s https://games.buttsstudios.com/ | grep -o 'Unlock Full[^<]*' | sort -u
  curl -s https://glb.buttsstudios.com/ | grep -o '<p class="price">[^/]*</span>' | head -1
  echo "Manual: test-mode purchase on each game -> lands with ?session_id= -> premium unlocks; a made-up cs_ id does not."
}

case "${1:-check}" in check) check;; fix) fix;; price) price;; verify) verify;;
  *) echo "usage: $0 check|fix|price|verify"; exit 2;; esac
