# iphone-duo-tracker
A GitHub Pages site shows where the iPhone Duo is in stock in Croatia and where to order it. A nightly CI workflow refreshes the page.

## Setup
1. In the repository settings, set Pages source to GitHub Actions.
2. Stores live in `retailers.json` as `{"name", "host", "feed", "order_url"}` entries (optional `variant`; a store without `order_url` takes the link from its feed items); `order_url` must be an https link on `host`. `feed` is an http(s) or file URL returning `{"as_of": "<ISO 8601 with timezone, optional>", "items": [{"variant", "availability", "order_url"}]}` where `availability` is `in_stock`, `out_of_stock` or `unknown`. A feed that cannot be read, or whose `as_of` is older than 86400 s, shows the store as unknown.
   The shipped stores (Links, Instar Informatika, HGSpot), their order pages and feed URLs are unverified best guesses, written without network access, and `product_verified` stays `false`; replace them with a checked list. Until their feeds exist the rows show unknown.
3. The `nightly` workflow rebuilds and deploys the page every night; run it by hand from the Actions tab. `python3 build.py` builds `site/` locally, and `python3 -m tests.check_page site/index.html` checks the built page.
