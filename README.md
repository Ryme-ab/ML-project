# Algerian Export ML Project

## Project Overview

Algeria's export economy is heavily concentrated in hydrocarbons, which accounted for approximately 92% of total exports in 2023. This project builds an end-to-end machine learning system that identifies, analyzes, and forecasts international export opportunities for Algerian exporters across agriculture, industry, and services sectors.

The system integrates multiple international trade datasets, applies clustering, classification, and forecasting models, and delivers insights through an interactive visualization dashboard aimed at supporting the Algerian Chamber of Commerce and Industry (CACI), the Ministry of External Commerce, exporters, and policymakers.

---

## Project Scope

### Time Range

2010 - 2023 (14 years)

- 2010-2019: pre-crisis baseline
- 2020-2021: COVID-19 disruption period
- 2022-2023: recovery period and most recent trends

### Target Countries (Partner List)

Algeria's current top export destinations plus major importers of Algeria's target products.
Final list target: approximately 25-30 countries.

Current Algerian export partners:

- France
- Italy
- Spain
- United Kingdom
- United States
- Turkey
- Brazil
- Netherlands
- Belgium
- Germany
- China
- Switzerland
- India
- Portugal
- Morocco

Strategic target markets (high import demand for Algeria's potential products):

- Saudi Arabia
- UAE
- Egypt
- Senegal
- Cote d'Ivoire
- Canada
- Japan
- South Korea
- Poland
- Czech Republic

### Product Scope

Work is performed at HS2 level for the full dataset and drills down to HS6 for priority products.

Priority HS sections:

| HS Code | Description |
|---------|-------------|
| HS07 | Edible vegetables (including dates) |
| HS08 | Edible fruit (citrus, figs) |
| HS15 | Animal/vegetable fats and oils (olive oil) |
| HS19 | Preparations of cereals, pastry |
| HS21 | Miscellaneous edible preparations |
| HS25 | Salt, sulphur, earth, stone (construction) |
| HS28 | Inorganic chemicals |
| HS31 | Fertilizers |
| HS68 | Articles of stone, plaster, cement |
| HS72 | Iron and steel |

### Reporter Country

- Country: Algeria
- ISO3 code: DZA
- UN Comtrade numeric code: 12

---

## Data Sources

| Source | What we use it for | Access |
|--------|---------------------|--------|
| UN Comtrade | Export/import values by product, country, year | Free API (100 req/hour) - comtrade.un.org |
| World Bank WITS | GDP, trade openness, economic indicators | Free API - wits.worldbank.org |
| WTO Statistics | Aggregate trade statistics, tariff data | Free CSV download - data.wto.org |
| ITC Trade Map | Cross-validation of trade flows | Manual CSV export - trademap.org |

### Data Access Notes

- UN Comtrade requires registration and an API subscription key. Store key in `.env` and never commit it.
- World Bank API is open and requires no key.
- ITC Trade Map may require institutional registration.
- All data used is public and compliant with data privacy requirements.

---

## Current Repository Structure

This is the active structure in this repository.

```text
algerian-export-ml/
  README.md
  requirements.txt
  .gitignore

  dashboard/
  data/
    raw/
      DATA_DESCRIPTION.md
      comtrade_algeria_exports.csv
      comtrade_world_imports.csv
      Trade_Map_-_List_of_importing_markets_for_a_product_exported_by_Algeria (1).csv
      worldbank/
      wto_algeria/
    interim/
    processed/

  models/

  notebooks/
    preporocessing/
      01_load_comtrade-checkpoint.ipynb
      02_load_worldbank-checkpoint.ipynb
      03_load_wto_trademap-checkpoint.ipynb
      04_master_integration-checkpoint.ipynb
    eda/
    forecasting/
    classification/
    clustring/

  reports/

  src/
    data/
    features/
    models/
    visualization/
```

Note: folder names `preporocessing` and `clustring` are kept as-is to match the current repository.

### Target Structure (Team Convention)

The team can progressively align toward the following production structure:

```text
project-root/
|
|-- README.md
|-- DATA_CONTRACT.md
|-- requirements.txt
|-- .env.example
|-- .gitignore
|
|-- data/
|   |-- raw/
|   |   |-- comtrade/
|   |   |-- worldbank/
|   |   |-- wto/
|   |   `-- trademap/
|   `-- processed/
|       |-- master_trade.parquet
|       |-- features.parquet
|       `-- labels.parquet
|
|-- notebooks/
|   |-- 00_data_collection/
|   |-- 01_preprocessing/
|   |-- 02_eda/
|   |-- 03_clustering/
|   |-- 04_classification/
|   `-- 05_forecasting/
|
|-- models/
|   |-- clustering/
|   |-- classification/
|   `-- forecasting/
|
|-- outputs/
|   |-- opportunity_ranking.csv
|   |-- cluster_assignments.csv
|   `-- forecasts.csv
|
|-- pipeline/
|   `-- run_pipeline.py
|
|-- dashboard/
|   |-- grafana/
|   |   |-- dashboard.json
|   |   `-- datasource.yaml
|   `-- sql/
|       |-- create_tables.sql
|       `-- queries/
|
`-- reports/
    |-- 01_introduction.md
    |-- 02_data_methodology.md
    |-- 03_feature_engineering.md
    |-- 04_clustering_results.md
    |-- 05_classification_results.md
    |-- 06_forecasting_results.md
    |-- 07_dashboard.md
    |-- 08_limitations.md
    `-- 09_conclusion.md
```

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Ryme-ab/ML-project.git
cd ML-project/algerian-export-ml
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
# Then open .env and fill in API keys
```

Windows PowerShell alternative:

```powershell
Copy-Item .env.example .env
```

### 5. Create raw data directories (if needed)

```bash
mkdir -p data/raw/comtrade data/raw/worldbank data/raw/wto data/raw/trademap
```

Windows PowerShell alternative:

```powershell
New-Item -ItemType Directory -Force -Path data/raw/comtrade, data/raw/worldbank, data/raw/wto, data/raw/trademap
```

### 6. Launch Jupyter

```bash
jupyter notebook
```

---

## Environment Variables

Create a `.env` file at the project root and never commit it.

```env
COMTRADE_API_KEY=your_key_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=algerian_exports
DB_USER=your_db_user
DB_PASSWORD=your_db_password
```

---

## Data Contract

All team members must read `DATA_CONTRACT.md` before writing preprocessing or modeling code.

The data contract defines the exact schema of processed data that data engineers produce and ML engineers consume, including column names, types, units, missing-value policy, and country code standards.

Key rules:

- All monetary values are in USD (raw units).
- Country codes use ISO 3166-1 alpha-3 throughout (example: DZA, FRA, CHN).
- Missing values are `NaN` and never represented as zero or empty string.
- Trade flow values of 0 represent real zero trade, not missing data.

---

## Git Workflow

### Branch Naming

```text
main                          demo-ready, team lead merges only
feature/data-collection       API scripts, raw downloaders
feature/data-pipeline         cleaning, merging, feature engineering
feature/eda                   exploratory analysis notebooks
feature/clustering            clustering model and notebook
feature/classification        classification model and notebook
feature/forecasting           forecasting model and notebook
feature/dashboard             Grafana config, DB setup, SQL
docs/report                   final report sections
```

### Start Working

```bash
git checkout main
git pull origin main
git checkout feature/your-branch
git pull origin feature/your-branch
# do your work
git add .
git commit -m "Add clear and specific commit message"
git push origin feature/your-branch
```

### Merge to main

1. Open a pull request from feature branch into `main`.
2. Add a concise change summary.
3. Team lead reviews and approves.
4. Team lead merges.

### Commit Message Rules

- Use present tense.
- Be specific and scoped.
- Avoid generic messages such as `update`, `changes`, or `wip`.

### Keep Branch Updated

```bash
git checkout feature/your-branch
git merge main
```

---

## Machine Learning Tasks

### Task 1 - Clustering

Goal: group countries by import-demand profile to identify coherent market segments.

- Algorithms: K-Means and/or Agglomerative Hierarchical Clustering
- Features: global demand index, trade growth rate, market-size vectors per product
- Evaluation: Silhouette Score, Davies-Bouldin Index
- Output: `cluster_assignments.csv` (country to cluster ID)

### Task 2 - Classification

Goal: label each country-product pair as high, medium, or low export opportunity.

- Algorithms: XGBoost or Random Forest
- Label definition:
  - High: market penetration ratio < 5% and global demand growth > 10% and product in Algeria export capacity
  - Medium: market penetration ratio < 15% and demand growth > 5%
  - Low: all other pairs
- Evaluation: Accuracy, Precision, Recall, F1-score (macro and per class)
- Output: `opportunity_ranking.csv` (pair ranking with predicted class and confidence)

### Task 3 - Forecasting

Goal: predict future trade volume and value by product-country pair.

- Algorithms: ARIMA baseline, Prophet, and optionally gradient boosting with lag features
- Split: 2010-2019 train, 2020-2021 validation, 2022-2023 test
- Evaluation: MAE, RMSE, MAPE
- Output: `forecasts.csv` with confidence intervals

---

## Dashboard

- Tool: Grafana (recommended) or Apache Superset
- Database: PostgreSQL
- Data flow: dashboard reads PostgreSQL tables populated by `pipeline/run_pipeline.py`

Required dashboard panels:

1. Export opportunity ranking (filter by country, product, sector)
2. Global demand trends (time series by product)
3. Predicted export growth by market (forecast output)
4. Priority market map (choropleth by opportunity score)
5. Historical versus forecasted trade comparison

---

## Existing Data Documentation

For complete raw dataset schema and column-level details, see:

- `data/raw/DATA_DESCRIPTION.md`
