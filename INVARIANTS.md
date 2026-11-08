# Invariants

## Listing
- Only retailers reporting iPhone Duo in stock appear on the page.
- Every listed retailer has a non-empty https order link on its own configured host.

## Refresh
- A failed fetch never changes the previously built page and the run exits non-zero.
- Deployment runs only after a successful build.

## Configuration
- Retailers are configuration and none are built in; the product name is configurable and marked unverified until confirmed.
