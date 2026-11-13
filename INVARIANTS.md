# Invariants

## Listing
[Listing](.jinni/features/iphone-duo-tracker.md)

## Refresh
[Refresh](.jinni/features/iphone-duo-tracker.md)

## Configuration
[Configuration](.jinni/features/iphone-duo-tracker.md)

## Published data
- A failed, empty or invalid fetch never replaces data/availability.json or the published page.
- Every publishing step in the refresh workflow runs only when the fetch step succeeded.

## Page content
- Every tracked store has a status, an ordering link and a visible last-refreshed time.
- Checkout checks read committed data only and never fetch live data.
