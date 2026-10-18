#!/usr/bin/env bash
# Deploy the new Butts Studios site (~/buttsstudios/site) as the main buttsstudios.com.
# Principal GO: 2026-10-14 ("yes we should deploy that oe now so that its the main site").
#
# Target: the existing Vercel project "website" (prj_J7pK4Ph2b6AVt03X6Pl7w0rNrU8W) that serves buttsstudios.com and
# www, so the domains stay attached. Needs a Vercel login that can see that team (run `vercel login` first).
#
#   bash ~/buttsstudios/scripts/deploy_new_site.sh          # dry run: checks + shows what would ship
#   bash ~/buttsstudios/scripts/deploy_new_site.sh --go     # deploy to production, verify, print rollback
set -euo pipefail
GO=${1:-}
ROOT="$HOME/buttsstudios"
SRC="$ROOT/site"
node "$ROOT/scripts/copy-lint.mjs" --root "$SRC"  # public-copy guard (COPY/LEGAL 2026-10-17); fails the deploy on a violation
ORG_ID="team_WMhVBeGTHA1CgDK9llwAmQd9"
PROJECT_ID="prj_J7pK4Ph2b6AVt03X6Pl7w0rNrU8W"
STAGE="$(mktemp -d)"
TOK=()
[ -n "${VERCEL_TOKEN:-}" ] && TOK=(--token "$VERCEL_TOKEN")

# Stage: the site folder only (no repo history, scripts or design sources). Archived pages and assets ride along.
rsync -a --exclude '_check*.html' --exclude '_open.html' --exclude '.DS_Store' --exclude '*.tmpl' "$SRC/" "$STAGE/"
cat > "$STAGE/vercel.json" <<'EOF'
{ "cleanUrls": false, "trailingSlash": false,
  "headers": [ { "source": "/assets/(.*)", "headers": [ { "key": "Cache-Control", "value": "public, max-age=604800" } ] } ] }
EOF
mkdir -p "$STAGE/.vercel"
printf '{"orgId":"%s","projectId":"%s"}\n' "$ORG_ID" "$PROJECT_ID" > "$STAGE/.vercel/project.json"
echo "staged $(find "$STAGE" -type f | wc -l | tr -d ' ') files, $(du -sh "$STAGE" | cut -f1)"

# Footer Shop link: only ship it once the shop is live (Principal: footer-only link between site and shop).
if [ "$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 https://store.buttsstudios.com)" != "200" ]; then
  find "$STAGE" -name '*.html' -exec perl -0pi -e 's#<!--ff-shop-->.*?<!--/ff-shop-->##gs; s# \&nbsp;·\&nbsp; <a href="https://store.buttsstudios.com">Shop</a>##g' {} +
  echo "store.buttsstudios.com not live: Shop footer link removed from this deploy"
fi
# Pre-flight content checks (public copy rules).
if grep -rliE '\bAHL\b|Anne Huntington|digital[- ]only|nothing ships' "$STAGE" --include='*.html' | grep -v '/work/'; then
  echo "BLOCKED: banned wording found (above)"; exit 1; fi
missing=0
for f in $(cd "$STAGE" && find . -name '*.html' -not -path './work/wham-studios/vendor/*'); do
  for ref in $(grep -oE '(src|href)="[^"#?:]+\.(webp|png|jpg|svg|css|js|mp4|webm|html)"' "$STAGE/$f" | sed -E 's/^(src|href)="//; s/"$//'); do
    [ -e "$(cd "$STAGE/$(dirname "$f")" && pwd)/$ref" ] || { echo "missing: $f -> $ref"; missing=1; }
  done
done
[ $missing = 0 ] || { echo "BLOCKED: missing assets"; exit 1; }
# Internal links/anchors, img alt, head meta, nav + footer on every page.
python3 "$ROOT/scripts/check_site_links.py" || { echo "BLOCKED: site checks failed (above)"; exit 1; }
# Legal fill-ins ([CONFIRM: address / governing-law state / refund windows; seller = Butts Studios per DECISIONS 2026-10-15]) and draft badges must be
# resolved before anything ships; they wait on Principal decisions in ~/jarvis/JARVIS QUESTIONS.md.
python3 "$ROOT/scripts/check_launch_ready.py" "$STAGE" || { echo "BLOCKED: legal placeholders remain"; exit 1; }
echo "pre-flight OK"

vercel whoami "${TOK[@]}" >/dev/null 2>&1 || { echo "Not logged in to Vercel. Run: vercel login"; exit 1; }
echo "vercel user: $(vercel whoami "${TOK[@]}" 2>/dev/null)"

# Remember the current production deployment for rollback.
PREV=$(VERCEL_ORG_ID=$ORG_ID VERCEL_PROJECT_ID=$PROJECT_ID vercel ls --prod "${TOK[@]}" 2>/dev/null | grep -oE 'https://[a-z0-9.-]+\.vercel\.app' | head -1 || true)
echo "current production deployment (rollback target): ${PREV:-unknown}"

# If the project's Root Directory is still "website" (the old site's folder), nest the upload to match.
RD=$(cd "$STAGE" && vercel project inspect "${TOK[@]}" 2>/dev/null | grep -iE 'Root Directory' | awk '{print $NF}' || true)
echo "project root directory: ${RD:-.}"
if [ -n "${RD:-}" ] && [ "$RD" != "." ] && [ "$RD" != "/" ]; then
  mkdir -p "$STAGE/__up/$RD" && (cd "$STAGE" && find . -mindepth 1 -maxdepth 1 ! -name __up ! -name .vercel -exec mv {} "__up/$RD/" \;)
  mv "$STAGE/.vercel" "$STAGE/__up/.vercel"; STAGE="$STAGE/__up"
fi


if [ "$GO" != "--go" ]; then echo "DRY RUN: add --go to deploy"; exit 0; fi

# Project settings may still point at the old "website" root directory or a build step; this deploy is a static
# upload of the staged folder, so override to no framework / no build.
URL=$(cd "$STAGE" && vercel deploy --prod --yes "${TOK[@]}" 2>/dev/null | tail -1)
echo "deployed: $URL"

sleep 20
ok=1
for p in / /slate.html /how-we-work.html /partnerships.html /portfolio.html /portfolio/chief.html /favicon.svg; do
  code=$(curl -s -o /dev/null -w '%{http_code}' "https://buttsstudios.com$p")
  echo "  $code  https://buttsstudios.com$p"; [ "$code" = 200 ] || ok=0
done
curl -s https://buttsstudios.com/ | grep -q 'brand-x' && echo "  new header (C5 logo) is live" || { echo "  WARNING: new header not seen yet (CDN?)"; ok=0; }
if [ $ok = 1 ]; then echo "VERIFIED LIVE"; else echo "CHECK FAILED: consider rollback"; fi
echo "Rollback: vercel rollback ${PREV:-<previous production URL from 'vercel ls --prod'>} --scope $ORG_ID"
