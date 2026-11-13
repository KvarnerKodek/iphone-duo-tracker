# iPhone Duo tracker

A GitHub Pages site shows where the iPhone Duo is in stock in Croatia and where to order it. A nightly CI workflow refreshes the page. The repository is private; the site is served by GitHub Pages built from a workflow. Nightly, a scheduled workflow fetches the Croatian retailers stock state and commits or deploys the refreshed page.

- Page lists Croatian stores with current iPhone Duo stock.
- Each listed store links to its iPhone Duo order page.
- A nightly CI workflow regenerates and publishes the Pages site.

```jinni-feature
{
  "feature_id": "feature-274b77ed02fdb71d4ed34ca25e36713a2ae23d04bcdb3ed762eeb9be5b224dc1",
  "description": "A GitHub Pages site shows where the iPhone Duo is in stock in Croatia and where to order it. A nightly CI workflow refreshes the page. The repository is private; the site is served by GitHub Pages built from a workflow. Nightly, a scheduled workflow fetches the Croatian retailers stock state and commits or deploys the refreshed page.",
  "desired_state": "A GitHub Pages site shows where the iPhone Duo is in stock in Croatia and where to order it, refreshed nightly by CI.",
  "changes": [
    {
      "condition_id": "tracker.stock-listed",
      "binding_id": null,
      "statement": "Page lists Croatian stores with current iPhone Duo stock.",
      "rubric": "The generated page has one row per Croatian store showing its iPhone Duo stock status and the timestamp of the data. A check fails on a store row with no status, or on stock data older than 86400 s. A store whose stock cannot be read shows as unknown, not in stock. After merge: an operator confirms the live Pages site lists current stock.",
      "evaluation": null,
      "measure": null,
      "reason": "The request requires the page to show Croatian stores and their current iPhone Duo stock. The space policy sets the data age limit at 86400 s."
    },
    {
      "condition_id": "tracker.order-links",
      "binding_id": null,
      "statement": "Each listed store links to its iPhone Duo order page.",
      "rubric": "A check parses the generated page and fails on any store row without a link, or whose link does not point to an iPhone Duo order page on that store's domain. After merge: an operator confirms each live link opens the order page.",
      "evaluation": null,
      "measure": null,
      "reason": "The request requires the page to say where to order the iPhone Duo. A link per store is the observable form of that."
    },
    {
      "condition_id": "tracker.nightly-refresh",
      "binding_id": null,
      "statement": "A nightly CI workflow regenerates and publishes the Pages site.",
      "rubric": "A check reads the repository's CI workflow and fails unless it has a scheduled nightly trigger, a step that regenerates the page from the stock data, and a step that publishes it to GitHub Pages. After merge: an operator confirms the first scheduled run updates the live site.",
      "evaluation": null,
      "measure": null,
      "reason": "The request requires a nightly CI workflow that refreshes the page. The captured repository has no workflow file at commit 66837c7."
    }
  ]
}
```
