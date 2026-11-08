# iphone-duo-tracker
A GitHub Pages site shows where the iPhone Duo is in stock in Croatia and where to order it. A nightly CI workflow refreshes the page.

## Setup
1. In the repository settings, set Pages source to GitHub Actions.
2. Add retailers to `retailers.json` as `{"name", "host", "feed"}` entries; `feed` is an http(s) or file URL returning `{"items": [{"variant", "availability", "order_url"}]}` where `availability` is `in_stock`, `out_of_stock` or `unknown`. The list ships empty.
3. The `nightly` workflow rebuilds and deploys the page every night; run it by hand from the Actions tab. `python3 build.py` builds `site/` locally.
