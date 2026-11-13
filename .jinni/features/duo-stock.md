# iPhone Duo stock tracker

```jinni-feature
{
  "changes": [
    {
      "condition_id": "duo-stock-listing",
      "description": "The Pages site shows, for each tracked Croatian store, whether iPhone Duo stock is available.",
      "evaluation": null,
      "measure": null,
      "reason": "The request asks the site to show where stock is available. This listing is the core output of the tracker.",
      "rubric": "Build the site from the checkout using the committed availability data. The generated page has one row per tracked store showing its availability status. After merge: an operator confirms the live Pages site shows current stock status for the Croatian stores.",
      "statement": "The site lists iPhone Duo stock status for each tracked Croatian store."
    },
    {
      "condition_id": "order-links",
      "description": "Every tracked Croatian store entry on the site links to a page where iPhone Duo can be ordered.",
      "evaluation": null,
      "measure": null,
      "reason": "The request says the site shows where to order. Each store needs a link to order from.",
      "rubric": "Build the site from the checkout. Every store row contains a link to an ordering URL taken from the availability data, and no row lacks one. After merge: an operator opens a sample of the links on the live site.",
      "statement": "Each listed store links to its iPhone Duo ordering page."
    },
    {
      "condition_id": "pages-publication",
      "description": "The built tracker site is deployed to GitHub Pages from this repository.",
      "evaluation": null,
      "measure": null,
      "reason": "The request names GitHub Pages as the hosting target.",
      "rubric": "The repository contains a GitHub Pages deployment workflow or configuration that publishes the built site output. After merge: the Pages URL serves the tracker page.",
      "statement": "The tracker site is published with GitHub Pages from this repository."
    },
    {
      "condition_id": "nightly-refresh",
      "description": "A CI workflow runs on a nightly schedule, regenerates the availability data, and publishes the updated site.",
      "evaluation": null,
      "measure": null,
      "reason": "The request requires the availability data to be refreshed by CI every night.",
      "rubric": "The CI workflow file defines a scheduled trigger that runs once per night, regenerates the availability data, rebuilds the site, and deploys it. After merge: a scheduled run completes on the default branch.",
      "statement": "A scheduled CI workflow refreshes availability data nightly."
    },
    {
      "condition_id": "stale-data-marked",
      "description": "The page states the time of the last successful data refresh. A failed refresh leaves the previously published data in place.",
      "evaluation": null,
      "measure": null,
      "reason": "Without a timestamp, visitors cannot tell whether the listed stock is current. A failed refresh must not replace good data with an empty result.",
      "rubric": "Build the site from the checkout. The page includes a last-refreshed timestamp taken from the availability data. The refresh step publishes new data only when fetching succeeds, so a failed run leaves the last successful data published. After merge: an operator confirms the timestamp on the live site matches the latest scheduled run.",
      "statement": "Each page shows when its availability data was last refreshed."
    }
  ],
  "desired_state": "Tracks iPhone Duo stock availability in Croatia on a GitHub Pages site that a nightly CI workflow refreshes.",
  "feature_id": "duo-stock",
  "parent_id": null
}
```
