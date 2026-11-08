# Stock tracker

## tracker.stock-listed
The page lists each Croatian retailer that reports iPhone Duo in stock, with its variant and availability. Retailers that are out of stock or whose state is unknown are not listed.

## tracker.order-links
Every listed retailer links to its iPhone Duo order page. The link is non-empty, uses https and is on the retailer's configured host; a build with any other in-stock link fails.

## tracker.nightly-refresh
A scheduled workflow runs nightly, fetches every configured retailer's stock, rebuilds the page and publishes it to GitHub Pages. The page shows the time of its last successful refresh. A failed fetch fails the run, the deploy does not start and the previously published page stays in place.
