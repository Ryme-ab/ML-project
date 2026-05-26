# Clustering Notebook Summary

The `clustering_model.ipynb` notebook performs **three unsupervised learning tasks** on Algeria's trade data to support export diversification policy.

---

## Task 1 — Product-Level Opportunity Classification (K-Means)

- **Input:** `algeria_features.csv` + `product_export.csv` (latest year only — 2024, ~5,198 products)
- **Features:** `Global_Demand`, `Untapped_Potential`, `Market_Share`, `Export_Growth_Rate` (log-transformed, clipped, standardised)
- **Method:** K-Means with automatic *k* selection via silhouette score (optimal k = 4)
- **Output:** Each HS6 product is labelled one of:
  - **High Opportunity** (12 products) — large global demand + Algeria already has market share
  - **Medium Opportunity** (646) — high demand, strong recent growth
  - **Niche / Emerging** (2,688) — moderate demand, negligible current share
  - **Low Priority** (1,852) — small global markets
- **Saved to:** `output/opportunity_clusters.csv`

---

## Task 2 — Country Macroeconomic Benchmarking (Agglomerative)

- **Input:** `04_master_country_year.csv` (5,375 country-year rows)
- **Features:** 6 pre-scaled macro indicators (GDP, GDP growth, GDP per capita, population, trade openness, import dependency)
- **Method:** Agglomerative clustering with Ward linkage; *k* chosen by silhouette (k = 2)
- **Purpose:** Identify which countries Algeria clusters with — if it sits among resource-dependent economies rather than diversified ones, it confirms the urgency of structural transformation
- **Saved to:** `output/country_clusters.csv`

---

## Task 3 — WTO Sector Archetype Discovery (DBSCAN)

- **Input:** `04_master_sector_year.csv` (181 sector-year rows, filtered to exclude "Total Merchandise" aggregate)
- **Features:** `global_demand_index_std`, `demand_growth_rate_pct_std`, `demand_3yr_ma_std`
- **Method:** DBSCAN with `eps` chosen via k-distance elbow plot; falls back to GMM if DBSCAN finds < 2 clusters
- **Purpose:** Separate **stable trade regimes** from **volatile/anomalous periods** (e.g., COVID-2020, oil price crashes). Noise points flag years that shouldn't inform trend-based policy
- **Saved to:** `output/sector_clusters.csv`

