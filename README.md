# Algerian Export ML

Comprehensive end-to-end toolkit for analyzing Algerian exports and identifying product/market opportunities using trade (COMTRADE/WTO) and macroeconomic (World Bank) data.

This repository contains data ingestion scripts and notebooks, preprocessing and feature engineering, modeling experiments (clustering & classification), model artifacts, a small dashboard integration, and helper scripts for loading results into databases.

Table of Contents
-----------------
- Project overview
- Quickstart
- Repository structure
- Data (raw → processed)
- Notebooks
- Models & experiments
- Dashboard
- Installation & environment
- Usage: prepare, run, evaluate
- Docker
- Testing & validation
- Troubleshooting
- Contributing
- License & contact

Project overview
----------------
Algerian Export ML builds reproducible pipelines and notebooks to:

- Ingest raw trade and macroeconomic data into `data/raw/`.
- Clean, normalize, and produce feature-engineered CSVs in `data/processed/`.
- Train clustering and classification models that identify product and market opportunities.
- Produce visual reports and a dashboard for stakeholder consumption.

Quickstart
----------
1. Create and activate a Python virtual environment, then install dependencies:

```bash
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

2. Inspect or set credentials (if required). If your project uses environment variables, copy and edit the template:

```powershell
copy .env.example .env
# edit .env to add COMTRADE_API_KEY, database URL, etc.
```

3. Prepare data either by running the preprocessing notebooks in order or by running the scripted pipeline (if available):

```bash
# Option A: run notebooks interactively
jupyter lab
# open and run notebooks in notebooks/preprocessing/ in order: 01 → 02 → 03 → 04

# Option B: run scripts (if provided)
# python src/pipeline/run_pipeline.py
```

4. Load processed outputs into Postgres (optional):

```bash
python import_to_postgres.py
```

Repository structure
--------------------
Top-level layout (key folders & files):

- `data/` — raw, interim and processed CSVs
    - `data/raw/` — original downloads (COMTRADE, WTO, WorldBank raw exports)
    - `data/interim/` — intermediate artifacts
    - `data/processed/` — cleaned and feature-engineered CSVs (master tables)
        - Example: [data/processed/04_master_country_year.csv](data/processed/04_master_country_year.csv)
        - Example: [data/processed/04_master_sector_year.csv](data/processed/04_master_sector_year.csv)
        - Example: [data/processed/02_worldbank_features.csv](data/processed/02_worldbank_features.csv)

- `notebooks/` — Jupyter notebooks for preprocessing, experiments, and reports
    - `notebooks/preprocessing/01_data_loading_and_cleaning.ipynb`
    - `notebooks/preprocessing/02_feature_engineering.ipynb`
    - `notebooks/preprocessing/03_scaling_and_normalization.ipynb`
    - `notebooks/preprocessing/04_master_integration_and_eda.ipynb`
    - `notebooks/classification/` — product & market classification experiments
    - `notebooks/clustring/` — clustering experiments

- `src/` — python modules and helper scripts (data ingestion, feature builders, model wrappers)

- `models/` — saved model artifacts and training outputs

- `dashboard/` — dashboard configuration, queries, and visualization assets

- `docker/` — `docker-compose.yml` for local services (db, optional notebook server)
    - `docker/docker-compose.yml`

- root scripts & files:
    - [import_to_postgres.py](import_to_postgres.py) — helper to push processed CSVs to Postgres
    - [test_db.py](test_db.py) — lightweight DB connectivity/validation script
    - `requirements.txt` — Python dependencies
    - `detailed-report.txt` — auto-generated summary of processed CSVs (headers & samples)

Data: raw → processed
----------------------
Overview:

- Raw sources live in `data/raw/` (COMTRADE, WTO, WorldBank, HS references).
- `notebooks/preprocessing/` and `src/data/` contain ingestion code to convert raw downloads into cleaned CSVs.
- Processed outputs are placed in `data/processed/` and are the canonical inputs for modeling and the dashboard.

Important processed files (examples):

- [data/processed/01_wto_cleaned.csv](data/processed/01_wto_cleaned.csv)
- [data/processed/02_worldbank_features.csv](data/processed/02_worldbank_features.csv)
- [data/processed/02_wto_demand_features.csv](data/processed/02_wto_demand_features.csv)
- [data/processed/03_diversification_scaled.csv](data/processed/03_diversification_scaled.csv)
- [data/processed/04_master_country_year.csv](data/processed/04_master_country_year.csv)
- [data/processed/04_master_sector_year.csv](data/processed/04_master_sector_year.csv)

Notebooks
---------
Notebooks are organized by task. Recommended workflow:

1. Run `01_data_loading_and_cleaning.ipynb` to populate `data/interim/` and `data/processed/`.
2. Run `02_feature_engineering.ipynb` to create derived features.
3. Run `03_scaling_and_normalization.ipynb` to produce scaled versions.
4. Run `04_master_integration_and_eda.ipynb` to merge master tables and run EDA.

Models & experiments
--------------------
- Clustering experiments: `notebooks/clustring/` produce cluster assignments used for market segmentation.
- Classification experiments: `notebooks/classification/` train models to identify opportunity-level labels.
- Model artifacts are saved under `models/` using folder conventions like `models/<experiment>/<checkpoint>/`.

Training & inference (example)

```bash
# train a model (example wrapper — replace with actual script)
python src/models/train.py --config config/train_product_classifier.yaml

# run inference on processed features
python src/models/predict.py --model models/product_classifier/2025-01-01 --input data/processed/04_master_sector_year.csv --output results/predictions.csv
```

Dashboard
---------
The `dashboard/` folder contains SQL and visualization config used to feed a BI tool. Use the processed CSVs or load them into Postgres (see below) for dashboarding.

Running with Docker (optional)
-----------------------------
A docker-compose is provided to run supporting services (e.g., Postgres) locally.

```bash
cd docker

```

After DB is up, run:

```bash
python import_to_postgres.py
python test_db.py
```

Installation & environment
--------------------------
1. Create virtual environment (see Quickstart).
2. Install dependencies: `pip install -r requirements.txt`.
3. (Optional) Use `pip install -e .` if the repo exposes a package entrypoint.

Usage: prepare, run, evaluate
------------------------------
- Prepare: ensure `data/raw/` contains the raw downloads or run ingestion scripts.
- Run: execute preprocessing notebooks or pipeline scripts in order.
- Load: use `python import_to_postgres.py` to push processed CSVs to Postgres.
- Evaluate: use notebooks in `notebooks/*` and `reports/` to reproduce analysis and figures.

Testing & validation
--------------------
- `test_db.py` contains simple connectivity checks. Run it after starting the DB:

```bash
python test_db.py
```

- Use pandas checks (row counts, dtype assertions) to validate processed files. Example snippet is available in `detailed-report.txt`.

Troubleshooting
---------------
- If notebooks fail due to missing packages, confirm `requirements.txt` and virtual environment activation.
- If ingestion scripts fail, verify API keys and the presence of expected raw files.
- For Postgres connection errors, check `docker/docker-compose.yml` and environment variables in `.env`.

Contributing
------------
- Use feature branches `feature/<short-desc>` and open a pull request describing changes.
- Keep notebooks deterministic: clear outputs before committing, and include executed checkpoints in `notebooks/*/results` when necessary.
- Add unit tests or validation scripts under `src/tests/` when adding new processing logic.

License & contact
-----------------
Check for a `LICENSE` file in the repository root. If none exists and you plan to publish, add an appropriate license (MIT/Apache-2.0 etc.).

Maintainer / Contact
- Primary maintainer: repository owner (see GitHub repo settings and collaborators).

Acknowledgements
----------------
Data sources: UN COMTRADE, WTO, and World Bank public datasets. HS reference tables are included under `data/raw/hs_reference/`.

Change log
----------
See git history for changes. For major updates, consider adding release notes under `reports/`.

Appendix: useful file references
-------------------------------
- Import helper: [import_to_postgres.py](import_to_postgres.py)
- DB tests: [test_db.py](test_db.py)
- Docker compose: [docker/docker-compose.yml](docker/docker-compose.yml)
- Detailed CSV summary: [detailed-report.txt](detailed-report.txt)

----
If you'd like, I can also:

- run the notebooks in order and report missing dependencies
- run `python import_to_postgres.py` to validate DB loading (requires credentials)
- create a short CONTRIBUTING.md or LICENSE file

Open a quick next step request or tell me which of the above actions you'd like me to run.
