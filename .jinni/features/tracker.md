# Stock tracker

## tracker.stock-listed
Page lists Croatian stores with current iPhone Duo stock.

## tracker.order-links
Each listed store links to its iPhone Duo order page. The link is non-empty, uses https and is on the store's configured host; a build with any other link fails.

## tracker.nightly-refresh
A Jinni-scheduled daily job runs refresh.sh, which fetches every configured store's stock and rebuilds the served page; the existing nightly workflow stays. A store whose feed cannot be read, or whose as_of is older than 86400 s, is listed as unknown. The page shows the time of its last successful refresh. A bad configuration or a failed render makes refresh.sh exit non-zero and the previously served page stays in place.
