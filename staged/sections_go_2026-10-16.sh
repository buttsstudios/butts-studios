#!/usr/bin/env bash
# Butts Studios sections + subdomains: one shared style. STAGED 2026-10-16, nothing deployed.
# Principal (2026-10-16): "different subsets like games etc should have a front page and if its has subdomains it
# should be styled in consistent manner even if slightly different".
#
# Modes:
#   preview   read-only dry run: per subdomain, repo, branch, base, commits it would publish, prerequisites, live state
#   go        GO-gated: push style/studios-sections-2026-10-16 to origin/main per repo (Vercel git deploys)
#   verify    read-only curls after a deploy: Studios bar + section attribute + legal links present
#   rollback  needs the Principal (2026-10-13 rule: fix forward): ROLLBACK_OK=principal; pushes the recorded old main
#
# Order (enforced by `go`):
#   1. The new buttsstudios.com is live (scripts/deploy_new_site.sh): the bar/footer link to /games.html, /books.html,
#      /video.html, /terms.html, /refunds.html, /privacy.html, which exist only on the new site.
#   2. Games repos (hub, glb, cards, puzzle) branch from the staged price/no-99 work, so staged/games_go_2026-10-15.sh
#      `fix` and `price` must be on origin/main first. The style branch is rebased onto the current price branch tip
#      (which then holds the filled Payment Links), and must not carry a __NEW_PAYMENT_LINK_ placeholder.
#   3. Film / animation / novels / clients branch from local main; they publish that one pending local commit too
#      (contact links moved off the dead butts-studios.com domain).
# Needs: buttsstudios GitHub push login (setup sheet). Projects not git-connected: `vercel --prod` from the worktree
# with the Butts Studios Vercel token (setup row vercel-butts-deploy).
set -euo pipefail
B=~/buttsstudios
BR=style/studios-sections-2026-10-16
# name:repo:base:host
T=("games-hub:games/portal:price/no-99-2026-10-15:games"
   "glb:games/glb:price/no-99-2026-10-15:glb"
   "cards:apps/butts-cards-next:price/no-99-2026-10-15:cards"
   "puzzle:apps/butts-puzzle-next:price/no-99-2026-10-15:puzzle"
   "film:production/film:main:film"
   "animation:production/animation:main:animation"
   "novels:publication/the-signal:main:novels"
   "clients:apps/butts-clients-next:main:clients")
LOG=$B/staged/sections_go_2026-10-16.log

gate() { [[ "${CONFIRM:-}" == "GO" ]] && return; read -r -p "Type GO to $1: " a; [[ "$a" == "GO" ]] || { echo "aborted"; exit 1; }; }
code() { curl -s -o /dev/null -m 15 -w '%{http_code}' "$1"; }

preview() {
  printf "%-10s %-28s %-24s %-6s %s\n" NAME REPO BASE LIVE "WOULD PUBLISH (origin/main..$BR)"
  for e in "${T[@]}"; do IFS=: read -r n r base h <<<"$e"
    git -C "$B/$r" rev-parse -q --verify "$BR" >/dev/null || { echo "MISS $n: no $BR"; continue; }
    git -C "$B/$r" fetch -q origin 2>/dev/null || echo "  (fetch failed for $r; showing local view)"
    printf "%-10s %-28s %-24s %-6s %s commits\n" "$n" "$r" "$base" "$(code "https://$h.buttsstudios.com/")" "$(git -C "$B/$r" rev-list --count "origin/main..$BR")"
    git -C "$B/$r" log --format='             %h %s' "origin/main..$BR"
    git -C "$B/$r" diff --stat "origin/main...$BR" | tail -1 | sed 's/^/             /'
    if [[ "$base" != main ]]; then
      git -C "$B/$r" merge-base --is-ancestor "$base" origin/main && echo "             prereq ok: $base is on origin/main" \
        || echo "             WAIT: $base not on origin/main yet (run staged/games_go_2026-10-15.sh fix + price first)"
    fi
    git -C "$B/$r" grep -q "__NEW_PAYMENT_LINK_" "$BR" 2>/dev/null && echo "             WAIT: Payment Link placeholder on $BR (rebases on go)"
  done
  echo "new site: games.html $(code https://buttsstudios.com/games.html) terms.html $(code https://buttsstudios.com/terms.html) (both must be 200 before go)"
  echo "local preview: open $B/staged/sections_preview/index.html"
}

go() {
  [[ "$(code https://buttsstudios.com/games.html)" == 200 && "$(code https://buttsstudios.com/terms.html)" == 200 ]] \
    || { echo "STOP: the new buttsstudios.com is not live yet (scripts/deploy_new_site.sh first)"; exit 1; }
  gate "push the shared Studios style to the 8 subdomains"
  for e in "${T[@]}"; do IFS=: read -r n r base h <<<"$e"
    git -C "$B/$r" fetch -q origin
    if [[ "$base" != main ]]; then
      git -C "$B/$r" merge-base --is-ancestor "$base" origin/main || { echo "SKIP $n: $base not live yet"; continue; }
      wt=$(mktemp -d); git -C "$B/$r" worktree add -q "$wt" "$BR"
      git -C "$wt" rebase -q "$base" || { git -C "$wt" rebase --abort; git -C "$B/$r" worktree remove --force "$wt"; echo "STOP $n: rebase conflict"; exit 1; }
      git -C "$B/$r" worktree remove "$wt"
    fi
    git -C "$B/$r" grep -q "__NEW_PAYMENT_LINK_" "$BR" && { echo "STOP $n: placeholder on $BR"; exit 1; }
    git -C "$B/$r" merge-base --is-ancestor origin/main "$BR" || { echo "STOP $n: $BR does not fast-forward origin/main"; exit 1; }
    echo "$(date -u +%FT%TZ) $n old_main=$(git -C "$B/$r" rev-parse origin/main) new=$(git -C "$B/$r" rev-parse "$BR")" >>"$LOG"
    git -C "$B/$r" push origin "$BR:main"
  done
  echo "pushed; wait for Vercel, then: $0 verify"
}

verify() {
  for e in "${T[@]}"; do IFS=: read -r n r base h <<<"$e"
    p=$(curl -s -m 15 "https://$h.buttsstudios.com/")
    ok=1; for s in 'class="bs-bar"' 'data-bs-section=' 'buttsstudios.com/terms.html' 'Butts Studios'; do grep -q "$s" <<<"$p" || { ok=0; echo "FAIL $n missing $s"; }; done
    grep -qi "9C27B0\|E91E63" <<<"$p" && echo "WARN $n still carries the old magenta"
    [[ $ok == 1 ]] && echo "ok   $n $(code "https://$h.buttsstudios.com/")"
  done
}

rollback() {
  [[ "${ROLLBACK_OK:-}" == principal ]] || { echo "STOP: rollback needs the Principal (fix forward is the rule): ROLLBACK_OK=principal"; exit 1; }
  for e in "${T[@]}"; do IFS=: read -r n r base h <<<"$e"
    old=$(grep " $n old_main=" "$LOG" | tail -1 | sed 's/.*old_main=\([0-9a-f]*\).*/\1/'); [[ -n "$old" ]] || continue
    git -C "$B/$r" push --force-with-lease origin "$old:main"
  done
}

case "${1:-preview}" in preview) preview;; go) go;; verify) verify;; rollback) rollback;; *) echo "usage: $0 preview|go|verify|rollback"; exit 2;; esac
