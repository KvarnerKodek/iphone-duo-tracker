# Stock tracker

## tracker.stock-listed
Page lists Croatian stores with current iPhone Duo stock.

## tracker.order-links
Every listed retailer links to its iPhone Duo order page. The link is non-empty, uses https and is on the retailer's configured host; a build with any other in-stock link fails.

## tracker.nightly-refresh
A Jinni-scheduled daily job runs refresh.sh, which fetches every configured retailer's stock and rebuilds the served page; the existing nightly workflow stays. The page shows the time of its last successful refresh. A failed fetch makes refresh.sh exit non-zero and the previously served page stays in place.
