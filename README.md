# Groundwork Landscaping — Site

Static site for groundworkllc.netlify.app. Sources are plain HTML in the repo root;
`build.py` assembles `dist/` for Netlify. See `check_links.py` for the
pre-deploy link/image checker.

---

## Analytics

Page counts come from Cloudflare Web Analytics — cookieless, so no consent banner.
It stays off until `CF_ANALYTICS_TOKEN` is set in Netlify → Site settings →
Environment variables; `build.py` injects the beacon only when the variable is
present (`CF_ANALYTICS_TOKEN=… python3 build.py` locally if you want to see it).

The notice cannot drift from the beacon: the paragraph between the
`analytics-policy` markers in `privacy.html` is swapped between the "no analytics"
and "Cloudflare Web Analytics" copy at build time, and the build fails rather than
publish a beacon the notice doesn't describe. Bump the notice's *Last updated*
date when the token lands.

Known limitation: pageviews only. It cannot attribute phone calls; form leads carry
`?src=` into the hidden `source` field and are readable per-channel in Formspree.

---

## Deployment

Every push and pull request runs `.github/workflows/ci.yml`: the link/image
checker (`check_links.py --quiet`) gates the build, then `dist/` is assembled
and uploaded as a build artifact. Pushes to `main` also attempt a Netlify deploy
(see below).

### Deploy to Netlify (one-time setup)

The site is served from `dist/` (`netlify.toml`). After `gh` is logged in as the
repo owner:

1. Get the **Site ID**: Netlify → Site settings → General → Site details.
2. Create a Netlify personal access token: Netlify account → Account settings →
   Access tokens → Create token (no special scopes needed).
3. Add the secrets in repo Settings → Secrets and variables → Actions:
   - `NETLIFY_SITE_ID` — the site ID from step 1
   - `NETLIFY_AUTH_TOKEN` — the token from step 2

Once both are set, the `deploy-netlify` job in `ci.yml` deploys `dist/` to
`groundworkllc.netlify.app` automatically on push to `main`. Until the secrets
are configured, the job fails loudly instead of deploying to the wrong site — a
manual fallback works too: `ntl deploy --prod` (after `ntl login`).

### GitHub Pages note

`latinlover11.github.io/grondworkco/` is also live via GitHub Pages (legacy
build from `main`). Deploying the Netlify site is the production path — this
repo's Netlify project uses `dist/`, while the Pages site builds from the repo
root. If you re-enable Pages, point it at `dist/` in repo Settings → Pages.

---

## Photo checklist