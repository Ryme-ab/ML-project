# Algerian Export ML Project

An end-to-end machine learning and analytics project focused on Algerian exports, combining trade flows with macroeconomic indicators to support:

- exploratory analysis,
- demand and export forecasting,
- classification and clustering use cases,
- dashboarding and reporting.

## 1. Project Goals

- Build a clean, analysis-ready dataset from multiple trade and macro sources.
- Identify high-potential products and destination markets.
- Forecast export-related trends using time-series models.
- Enable reproducible experimentation through a structured project layout.

## 2. Data Sources

The project currently integrates raw CSV files from:

- UN Comtrade
	- `data/raw/comtrade_algeria_exports.csv`
	- `data/raw/comtrade_world_imports.csv`
- ITC Trade Map
	- `data/raw/Trade_Map_-_List_of_importing_markets_for_a_product_exported_by_Algeria (1).csv`
- WTO
	- `data/raw/wto_algeria/WtoData_20260325191317.csv`
- World Bank (WDI indicators + metadata)
	- `data/raw/worldbank/...`

For complete per-file schema and column lists, see:

- `data/raw/DATA_DESCRIPTION.md`

## 3. Repository Structure

```text
algerian-export-ml/
	dashboard/                 # Dashboard app code (currently empty)
	data/
		raw/                     # Original source files
		interim/                 # Intermediate transformed files
		processed/               # Final cleaned/model-ready datasets
	models/                    # Saved model artifacts (currently empty)
	notebooks/
		preporocessing/          # Data loading/cleaning/integration notebooks
		eda/                     # Exploratory analysis notebooks
		forecasting/             # Time-series forecasting notebooks
		classification/          # Classification experiments
		clustring/               # Clustering experiments
	reports/                   # Figures, summaries, and final outputs
	src/
		data/                    # Data ingestion/transformation scripts
		features/                # Feature engineering logic
		models/                  # Training/inference code
		visualization/           # Plotting and reporting helpers
	requirements.txt
	README.md
```

Note: Folder names `preporocessing` and `clustring` are preserved as-is to match the current repository.

## 4. Environment Setup

### Prerequisites

- Python 3.10+ (project tested with modern Python environments)
- `pip`

### Installation

```bash
# from repository root
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

## 5. How To Run

### Option A: Notebook Workflow (recommended currently)

1. Start Jupyter:

```bash
jupyter notebook
```

2. Run preprocessing notebooks in this order:

- `notebooks/preporocessing/01_load_comtrade-checkpoint.ipynb`
- `notebooks/preporocessing/02_load_worldbank-checkpoint.ipynb`
- `notebooks/preporocessing/03_load_wto_trademap-checkpoint.ipynb`
- `notebooks/preporocessing/04_master_integration-checkpoint.ipynb`

3. Continue with notebooks in:

- `notebooks/eda/`
- `notebooks/forecasting/`
- `notebooks/classification/`
- `notebooks/clustring/`

### Option B: Scripted Pipeline (if you add Python modules under `src/`)

Typical command pattern:

```bash
python -m src.data.<module_name>
python -m src.features.<module_name>
python -m src.models.<module_name>
```

## 6. Current Pipeline Outputs

Based on existing notebook workflow, expected processed outputs include:

- `data/processed/comtrade_clean.csv`
- `data/processed/comtrade_world_imports_clean.csv`

You can add additional merged feature tables in `data/processed/` as integration steps expand.

## 7. Modeling Scope

The installed dependencies indicate support for:

- Classical ML: scikit-learn, xgboost, lightgbm
- Time series: prophet, statsmodels
- Analysis and plotting: pandas, numpy, matplotlib, seaborn, plotly

Suggested modeling tracks:

- Forecast export value by product and market.
- Classify product-market opportunities (high/medium/low potential).
- Cluster destination countries by macro and trade profile.

## 8. Dashboard And API

Dependencies include FastAPI and Uvicorn, and a `dashboard/` folder exists.

Recommended next implementation:

- Build API endpoints in `src/models/` or a dedicated `api/` package.
- Add dashboard app code under `dashboard/`.
- Serve inference results and KPI charts from processed/model outputs.

## 9. Reproducibility Checklist

- Keep raw source files immutable in `data/raw/`.
- Version all transformed outputs in `data/interim/` and `data/processed/` with clear naming.
- Save model artifacts in `models/` with timestamp + model metadata.
- Track experiments and metrics in `reports/`.
- Document schema changes in `data/raw/DATA_DESCRIPTION.md` (and optionally equivalent docs for interim/processed).

## 10. Troubleshooting

- Missing packages: run `pip install -r requirements.txt` again in the active environment.
- Notebook path issues: launch Jupyter from repository root so relative paths like `../data/raw/...` resolve correctly.
- Encoding errors on CSV load: try `encoding='utf-8-sig'` first, then `cp1252` for legacy exports.

## 11. Roadmap

- Add production-ready scripts under `src/` for each notebook stage.
- Add train/validation/test splitting and experiment tracking.
- Add model evaluation reports and feature importance artifacts.
- Add dashboard UI and API integration.
- Add CI checks for linting, tests, and data schema validation.

## 12. Authors

Project owner: DELL (local workspace owner)

You can replace this section with your name/team and contact details.

## 13. License

No license file is currently present.

If this project will be shared publicly, add a `LICENSE` file (for example MIT or Apache-2.0) and update this section.
