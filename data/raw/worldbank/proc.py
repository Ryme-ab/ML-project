"""
=============================================================================
 BACI + World Bank — Full Preprocessing Pipeline
 ENSIA ML Project 2025-2026 | Algerian Export Opportunity Analysis
=============================================================================

 Directory structure expected:
   data/
     raw/
       baci/
         BACI_HS17_Y2010_V202601.csv   (one file per year)
         BACI_HS17_Y2011_V202601.csv
         ...
         BACI_HS17_Y2023_V202601.csv
         country_codes_V202601.csv     (BACI country reference)
         product_codes_HS17_V202601.csv (BACI product reference)
       worldbank/
         WDI_Data.csv                  (World Bank WDI bulk download)
     processed/
       (output files go here)

 Run:
   pip install pandas numpy pyarrow tqdm country-converter
   python preprocessing.py
=============================================================================
"""

import os
import glob
import warnings
import numpy as np
import pandas as pd
from tqdm import tqdm
import country_converter as coco

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────

RAW_BACI_DIR    = "data/raw/baci/"
RAW_WB_DIR      = "/worldbank/"
PROCESSED_DIR   = "data/processed/"

ALGERIA_ISO3    = "DZA"          # Algeria's ISO-3 code
ALGERIA_BACI_ID = 12             # Algeria's numeric code in BACI (i column)

# Years to keep (adjust to match your downloaded files)
YEAR_START = 2010
YEAR_END   = 2023

# World Bank indicators to keep
WB_INDICATORS = {
    "NY.GDP.MKTP.CD"   : "gdp_usd",           # GDP (current USD)
    "NY.GDP.PCAP.CD"   : "gdp_per_capita_usd", # GDP per capita
    "NE.TRD.GNFS.ZS"   : "trade_openness_pct", # Trade (% of GDP)
    "SP.POP.TOTL"      : "population",          # Population
    "TM.VAL.MRCH.CD.WT": "imports_total_usd",  # Merchandise imports (USD)
    "TX.VAL.MRCH.CD.WT": "exports_total_usd",  # Merchandise exports (USD)
}

os.makedirs(PROCESSED_DIR, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — LOAD RAW BACI FILES
# ─────────────────────────────────────────────────────────────────────────────

def load_baci(raw_dir: str, year_start: int, year_end: int) -> pd.DataFrame:
    """
    Read all BACI annual CSV files and concatenate into one DataFrame.

    BACI columns:
        t  : year
        i  : exporter (numeric country code)
        j  : importer (numeric country code)
        k  : product (HS6 code as string, zero-padded to 6 digits)
        v  : trade value (thousands USD)
        q  : quantity (metric tons)
    """
    files = sorted(glob.glob(os.path.join(raw_dir, "BACI_HS17_Y*.csv")))
    frames = []

    for f in tqdm(files, desc="Loading BACI CSVs"):
        year = int(os.path.basename(f).split("_Y")[1][:4])
        if not (year_start <= year <= year_end):
            continue

        df = pd.read_csv(
            f,
            dtype={"k": str},   # keep HS codes as strings (leading zeros)
            low_memory=False,
        )
        df.columns = df.columns.str.strip()
        frames.append(df)

    baci = pd.concat(frames, ignore_index=True)
    print(f"  Loaded {len(baci):,} rows | years {year_start}–{year_end}")
    return baci


def load_baci_references(raw_dir: str):
    """Load country and product code lookup tables shipped with BACI."""
    countries = pd.read_csv(
        os.path.join(raw_dir, "country_codes_V202601.csv"),
        dtype=str,
    )
    products = pd.read_csv(
        os.path.join(raw_dir, "product_codes_HS17_V202601.csv"),
        dtype={"code": str},
    )
    return countries, products


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — FILTER & CLEAN BACI
# ─────────────────────────────────────────────────────────────────────────────

def clean_baci(baci: pd.DataFrame, algeria_id: int) -> pd.DataFrame:
    """
    Filter to Algeria as exporter, enforce types, remove bad rows.

    Strategy:
    - Keep rows where i == Algeria's BACI numeric code.
    - Also keep the global import dataset (all j values) so we can
      compute global demand for each product — needed for the
      Global Demand Index feature later.
    We return two DataFrames: algerian exports and global imports.
    """

    # ── 2a. Fix HS code: zero-pad to 6 digits
    baci["k"] = baci["k"].astype(str).str.strip().str.zfill(6)

    # ── 2b. Enforce numeric types
    for col in ["t", "i", "j", "v", "q"]:
        baci[col] = pd.to_numeric(baci[col], errors="coerce")

    # ── 2c. Drop rows with any null in core columns
    before = len(baci)
    baci.dropna(subset=["t", "i", "j", "k", "v"], inplace=True)
    print(f"  Dropped {before - len(baci):,} rows with nulls in core columns")

    # ── 2d. Drop zero-value trade flows (uninformative)
    baci = baci[baci["v"] > 0].copy()

    # ── 2e. Cast year and country codes to int
    baci["t"] = baci["t"].astype(int)
    baci["i"] = baci["i"].astype(int)
    baci["j"] = baci["j"].astype(int)

    # ── 2f. Outlier removal: remove top 0.1% extreme values per year
    #   (data entry errors in trade databases are common at extreme ends)
    threshold = baci.groupby("t")["v"].transform(lambda x: x.quantile(0.999))
    baci = baci[baci["v"] <= threshold].copy()

    # ── 2g. Split into Algeria exports vs. global imports
    algeria_exports = baci[baci["i"] == algeria_id].copy()
    global_imports  = baci.copy()   # all flows — used to compute world demand

    print(f"  Algeria export rows  : {len(algeria_exports):,}")
    print(f"  Global flow rows     : {len(global_imports):,}")
    return algeria_exports, global_imports


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — HS CODE MAPPING (products → sector / chapter labels)
# ─────────────────────────────────────────────────────────────────────────────

# HS chapters mapped to broad economic sectors.
# Source: UN HS 2017 edition chapter list (chapters 1–99).
HS_CHAPTER_TO_SECTOR = {
    **{str(c).zfill(2): "Agriculture & Food"      for c in list(range(1, 25))},
    **{str(c).zfill(2): "Minerals & Energy"       for c in list(range(25, 28))},
    **{str(c).zfill(2): "Chemicals"               for c in list(range(28, 39))},
    **{str(c).zfill(2): "Plastics & Rubber"       for c in list(range(39, 41))},
    **{str(c).zfill(2): "Leather & Hides"         for c in list(range(41, 44))},
    **{str(c).zfill(2): "Wood & Paper"            for c in list(range(44, 50))},
    **{str(c).zfill(2): "Textiles & Apparel"      for c in list(range(50, 64))},
    **{str(c).zfill(2): "Footwear & Accessories"  for c in list(range(64, 68))},
    **{str(c).zfill(2): "Stone & Glass"           for c in list(range(68, 71))},
    **{str(c).zfill(2): "Metals"                  for c in list(range(72, 84))},
    **{str(c).zfill(2): "Machinery & Electronics" for c in list(range(84, 86))},
    **{str(c).zfill(2): "Transport Equipment"     for c in list(range(86, 90))},
    **{str(c).zfill(2): "Precision Instruments"   for c in list(range(90, 93))},
    **{str(c).zfill(2): "Miscellaneous"           for c in list(range(93, 100))},
    "71": "Precious Metals & Gems",
}


def add_hs_labels(df: pd.DataFrame, products_ref: pd.DataFrame) -> pd.DataFrame:
    """
    Add human-readable product descriptions and sector groupings.

    Args:
        df          : DataFrame with column 'k' (HS6 string)
        products_ref: BACI product lookup table (columns: code, description)
    """
    # Extract HS chapter (first 2 digits) and section (first 4 digits)
    df["hs_chapter"] = df["k"].str[:2]
    df["hs_section"] = df["k"].str[:4]

    # Map to sector label
    df["sector"] = df["hs_chapter"].map(HS_CHAPTER_TO_SECTOR).fillna("Other")

    # Merge product descriptions from BACI reference file
    products_ref = products_ref.rename(columns={"code": "k", "description": "product_desc"})
    products_ref["k"] = products_ref["k"].astype(str).str.zfill(6)
    df = df.merge(products_ref[["k", "product_desc"]], on="k", how="left")

    return df


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — FEATURE ENGINEERING
# ─────────────────────────────────────────────────────────────────────────────

def engineer_features(
    algeria_exports: pd.DataFrame,
    global_imports: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute the core ML features needed for clustering, classification,
    and forecasting.

    Features produced (per Algeria–product–importer–year):
        export_value_usd    : v * 1000 (converted from thousands USD)
        export_qty_tons     : q (metric tons)
        yoy_growth_rate     : year-over-year growth of export value
        world_import_value  : total world imports of this product in this year
        market_share_pct    : Algeria's share of world imports (%)
        global_demand_index : normalised world import demand (0–1 scale per product)
        algerian_penetration: whether Algeria already exports this product to importer
        hhi_exporter        : Herfindahl–Hirschman Index of exporters for this product
                              (lower = more competitive market = harder to enter)
    """

    # ── 4a. Unit conversion
    algeria_exports = algeria_exports.copy()
    algeria_exports["export_value_usd"] = algeria_exports["v"] * 1000
    algeria_exports["export_qty_tons"]  = algeria_exports["q"]

    # ── 4b. Year-over-year growth rate of export value
    #   Sort by (product, importer, year) then compute pct change
    algeria_exports.sort_values(["k", "j", "t"], inplace=True)
    algeria_exports["yoy_growth_rate"] = (
        algeria_exports.groupby(["k", "j"])["export_value_usd"]
        .pct_change()
        .replace([np.inf, -np.inf], np.nan)
    )

    # ── 4c. World import value per (product, year)
    #   Sum all importer flows in global dataset
    world_demand = (
        global_imports.groupby(["k", "t"])["v"]
        .sum()
        .reset_index()
        .rename(columns={"v": "world_import_value_kUSD"})
    )
    world_demand["world_import_value_usd"] = world_demand["world_import_value_kUSD"] * 1000
    world_demand.drop(columns=["world_import_value_kUSD"], inplace=True)

    algeria_exports = algeria_exports.merge(world_demand, on=["k", "t"], how="left")

    # ── 4d. Algeria's market share (%) per product per year
    #   = Algeria total exports of product k in year t / world imports of k in t
    algeria_product_year = (
        algeria_exports.groupby(["k", "t"])["export_value_usd"]
        .sum()
        .reset_index()
        .rename(columns={"export_value_usd": "dz_total_export_usd"})
    )
    algeria_exports = algeria_exports.merge(algeria_product_year, on=["k", "t"], how="left")
    algeria_exports["market_share_pct"] = (
        algeria_exports["dz_total_export_usd"]
        / algeria_exports["world_import_value_usd"]
        * 100
    ).clip(0, 100)

    # ── 4e. Global Demand Index (normalised 0–1 per product across years)
    #   Shows whether world demand for this product is rising or falling
    min_demand = world_demand.groupby("k")["world_import_value_usd"].transform("min")
    max_demand = world_demand.groupby("k")["world_import_value_usd"].transform("max")
    world_demand["global_demand_index"] = (
        (world_demand["world_import_value_usd"] - min_demand)
        / (max_demand - min_demand + 1e-9)
    )
    algeria_exports = algeria_exports.merge(
        world_demand[["k", "t", "global_demand_index"]], on=["k", "t"], how="left"
    )

    # ── 4f. HHI (Herfindahl–Hirschman Index) of exporters per (product, year)
    #   Measures how concentrated the global supply is.
    #   High HHI (close to 1) = dominated by few exporters = hard market to enter.
    def compute_hhi(group):
        total = group["v"].sum()
        if total == 0:
            return np.nan
        shares = group["v"] / total
        return (shares ** 2).sum()

    hhi = (
        global_imports.groupby(["k", "t"])
        .apply(compute_hhi)
        .reset_index()
        .rename(columns={0: "hhi_exporter"})
    )
    algeria_exports = algeria_exports.merge(hhi, on=["k", "t"], how="left")

    # ── 4g. Algerian penetration flag (1 if Algeria exports to this importer at all)
    algeria_exports["algerian_penetration"] = (
        algeria_exports["export_value_usd"] > 0
    ).astype(int)

    # ── 4h. Drop intermediate helper columns
    algeria_exports.drop(columns=["dz_total_export_usd", "v", "q"], inplace=True)

    return algeria_exports


# ─────────────────────────────────────────────────────────────────────────────
# STEP 5 — LOAD & CLEAN WORLD BANK DATA
# ─────────────────────────────────────────────────────────────────────────────

def load_worldbank(wb_dir: str, indicators: dict, year_start: int, year_end: int) -> pd.DataFrame:
    """
    Load World Bank WDI bulk CSV, pivot to wide format, and clean.

    The WDI bulk download has this structure:
        Country Name | Country Code | Indicator Name | Indicator Code | 1960 | 1961 | ... | 2023

    We pivot it to:
        iso3 | year | gdp_usd | gdp_per_capita_usd | trade_openness_pct | ...
    """
    wb_path = os.path.join(wb_dir, "WDI_Data.csv")
    wb_raw  = pd.read_csv(wb_path, low_memory=False)

    # Keep only the indicators we need
    wb_raw = wb_raw[wb_raw["Indicator Code"].isin(indicators.keys())].copy()

    # Melt from wide (year columns) to long format
    year_cols = [str(y) for y in range(year_start, year_end + 1)]
    available_year_cols = [c for c in year_cols if c in wb_raw.columns]

    wb_long = wb_raw.melt(
        id_vars=["Country Code", "Indicator Code"],
        value_vars=available_year_cols,
        var_name="year",
        value_name="value",
    )

    wb_long["year"]  = wb_long["year"].astype(int)
    wb_long["value"] = pd.to_numeric(wb_long["value"], errors="coerce")

    # Pivot to wide (one column per indicator)
    wb_wide = wb_long.pivot_table(
        index=["Country Code", "year"],
        columns="Indicator Code",
        values="value",
        aggfunc="first",
    ).reset_index()

    # Rename columns to human-readable names
    wb_wide.rename(
        columns={"Country Code": "iso3", **indicators},
        inplace=True,
    )
    wb_wide.columns.name = None

    # ── 5a. Fill missing values
    #   Strategy: for each country, interpolate linearly across years,
    #   then forward-fill and back-fill edge years.
    wb_wide.sort_values(["iso3", "year"], inplace=True)
    indicator_cols = list(indicators.values())

    wb_wide[indicator_cols] = (
        wb_wide.groupby("iso3")[indicator_cols]
        .transform(lambda s: s.interpolate(method="linear").ffill().bfill())
    )

    # ── 5b. Standardise ISO3 codes using country-converter
    #   (World Bank uses some non-standard codes like XKX for Kosovo)
    cc = coco.CountryConverter()
    wb_wide["iso3_std"] = cc.convert(wb_wide["iso3"].tolist(), to="ISO3", not_found=None)
    wb_wide = wb_wide[wb_wide["iso3_std"].notna()].copy()
    wb_wide.drop(columns=["iso3"], inplace=True)
    wb_wide.rename(columns={"iso3_std": "iso3"}, inplace=True)

    print(f"  World Bank: {wb_wide.shape[0]:,} rows | {wb_wide['iso3'].nunique()} countries")
    return wb_wide


# ─────────────────────────────────────────────────────────────────────────────
# STEP 6 — MERGE BACI + WORLD BANK
# ─────────────────────────────────────────────────────────────────────────────

def merge_datasets(
    baci_features: pd.DataFrame,
    worldbank: pd.DataFrame,
    baci_countries: pd.DataFrame,
) -> pd.DataFrame:
    """
    Join BACI Algeria exports with World Bank indicators on (importer country, year).

    We add WB indicators for the IMPORTER (j) — this is the relevant market
    context for export opportunity analysis (their GDP, trade openness, etc.).
    """

    # ── 6a. Map BACI numeric importer codes → ISO3
    baci_countries = baci_countries.copy()
    baci_countries.columns = baci_countries.columns.str.strip()

    # BACI country file has columns: country_code, country_iso3, country_name
    code_col = [c for c in baci_countries.columns if "code" in c.lower()][0]
    iso3_col = [c for c in baci_countries.columns if "iso" in c.lower()][0]
    name_col = [c for c in baci_countries.columns if "name" in c.lower()][0]

    baci_countries[code_col] = pd.to_numeric(baci_countries[code_col], errors="coerce")
    code_to_iso3 = baci_countries.set_index(code_col)[iso3_col].to_dict()
    code_to_name = baci_countries.set_index(code_col)[name_col].to_dict()

    baci_features["importer_iso3"] = baci_features["j"].map(code_to_iso3)
    baci_features["importer_name"] = baci_features["j"].map(code_to_name)

    # ── 6b. Merge World Bank indicators (for importer)
    merged = baci_features.merge(
        worldbank,
        left_on=["importer_iso3", "t"],
        right_on=["iso3", "year"],
        how="left",
    )
    merged.drop(columns=["iso3", "year"], inplace=True, errors="ignore")

    # ── 6c. Validate coverage
    wb_coverage = merged["gdp_usd"].notna().mean() * 100
    print(f"  WB indicator coverage: {wb_coverage:.1f}% of rows matched")

    if wb_coverage < 50:
        print("  WARNING: Low World Bank match rate. Check country code alignment.")

    return merged


# ─────────────────────────────────────────────────────────────────────────────
# STEP 7 — FINAL CLEANING & SAVE
# ─────────────────────────────────────────────────────────────────────────────

def final_clean_and_save(df: pd.DataFrame, out_dir: str) -> pd.DataFrame:
    """
    Final cleaning pass, column reordering, and export.
    """
    df = df.copy()

    # ── 7a. Rename year column for clarity
    df.rename(columns={"t": "year", "j": "importer_code", "k": "hs6_code"}, inplace=True)

    # ── 7b. Drop rows where importer has no ISO3 (usually aggregates like "World")
    before = len(df)
    df.dropna(subset=["importer_iso3"], inplace=True)
    print(f"  Dropped {before - len(df):,} rows with unresolvable importer codes")

    # ── 7c. Reorder columns logically
    id_cols      = ["year", "hs6_code", "hs_chapter", "hs_section", "sector",
                    "product_desc", "importer_code", "importer_iso3", "importer_name"]
    trade_cols   = ["export_value_usd", "export_qty_tons", "yoy_growth_rate"]
    market_cols  = ["world_import_value_usd", "global_demand_index",
                    "market_share_pct", "hhi_exporter", "algerian_penetration"]
    wb_cols      = ["gdp_usd", "gdp_per_capita_usd", "trade_openness_pct",
                    "population", "imports_total_usd", "exports_total_usd"]

    all_cols = id_cols + trade_cols + market_cols + wb_cols
    existing_cols = [c for c in all_cols if c in df.columns]
    df = df[existing_cols]

    # ── 7d. Final dtype optimisations (reduce memory)
    df["year"]           = df["year"].astype("int16")
    df["hs6_code"]       = df["hs6_code"].astype("category")
    df["sector"]         = df["sector"].astype("category")
    df["importer_iso3"]  = df["importer_iso3"].astype("category")

    # ── 7e. Save
    csv_path     = os.path.join(out_dir, "algeria_export_features.csv")
    parquet_path = os.path.join(out_dir, "algeria_export_features.parquet")

    df.to_csv(csv_path, index=False)
    df.to_parquet(parquet_path, index=False, engine="pyarrow", compression="snappy")

    print(f"\n  Saved CSV     : {csv_path}  ({os.path.getsize(csv_path)/1e6:.1f} MB)")
    print(f"  Saved Parquet : {parquet_path}  ({os.path.getsize(parquet_path)/1e6:.1f} MB)")
    print(f"  Final dataset : {len(df):,} rows × {df.shape[1]} columns")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# OPTIONAL — ALSO BUILD GLOBAL DEMAND DATASET (for clustering/classification)
# ─────────────────────────────────────────────────────────────────────────────

def build_global_demand_dataset(
    global_imports: pd.DataFrame,
    products_ref: pd.DataFrame,
    worldbank: pd.DataFrame,
    baci_countries: pd.DataFrame,
    out_dir: str,
    year_start: int,
    year_end: int,
) -> pd.DataFrame:
    """
    Build a separate dataset of global import demand per (product, importer, year).
    This is used to:
    - Cluster importers by what they buy (for market segmentation)
    - Classify country-product pairs as high/medium/low opportunity
      (even if Algeria does NOT currently export there — the positive class
       is constructed from world import patterns, not just Algeria's flows)
    """
    print("\nBuilding global demand dataset...")

    df = global_imports.copy()
    df["import_value_usd"] = df["v"] * 1000

    # Keep only target years
    df = df[(df["t"] >= year_start) & (df["t"] <= year_end)]

    # Add HS labels
    df = add_hs_labels(df, products_ref)

    # Compute world total per (product, year) for share calculation
    world_total = df.groupby(["k", "t"])["import_value_usd"].sum().reset_index()
    world_total.rename(columns={"import_value_usd": "world_total_usd"}, inplace=True)
    df = df.merge(world_total, on=["k", "t"], how="left")
    df["importer_share_pct"] = df["import_value_usd"] / df["world_total_usd"] * 100

    # Map importer codes to ISO3
    code_col = [c for c in baci_countries.columns if "code" in c.lower()][0]
    iso3_col = [c for c in baci_countries.columns if "iso" in c.lower()][0]
    baci_countries[code_col] = pd.to_numeric(baci_countries[code_col], errors="coerce")
    code_to_iso3 = baci_countries.set_index(code_col)[iso3_col].to_dict()
    df["importer_iso3"] = df["j"].map(code_to_iso3)

    # Merge WB indicators
    df = df.merge(worldbank, left_on=["importer_iso3", "t"], right_on=["iso3", "year"], how="left")

    # Save
    path = os.path.join(out_dir, "global_demand_features.parquet")
    df.to_parquet(path, index=False, engine="pyarrow", compression="snappy")
    print(f"  Saved: {path}  ({os.path.getsize(path)/1e6:.1f} MB)")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# DIAGNOSTICS — Quick EDA summary after preprocessing
# ─────────────────────────────────────────────────────────────────────────────

def print_diagnostics(df: pd.DataFrame):
    print("\n" + "=" * 60)
    print("DATASET DIAGNOSTICS")
    print("=" * 60)
    print(f"Shape             : {df.shape}")
    print(f"Year range        : {df['year'].min()} – {df['year'].max()}")
    print(f"Unique products   : {df['hs6_code'].nunique():,}")
    print(f"Unique importers  : {df['importer_iso3'].nunique()}")
    print(f"Sectors           :\n{df['sector'].value_counts().to_string()}")
    print(f"\nMissing values (%):")
    missing = df.isnull().mean() * 100
    print(missing[missing > 0].round(2).to_string())
    print(f"\nTop 10 importers by total export value:")
    top_importers = (
        df.groupby("importer_iso3")["export_value_usd"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    print(top_importers.apply(lambda x: f"${x/1e9:.2f}B").to_string())
    print(f"\nTop 10 products by export value:")
    top_products = (
        df.groupby(["hs6_code", "product_desc"])["export_value_usd"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    print(top_products.apply(lambda x: f"${x/1e9:.2f}B").to_string())


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("STEP 1 — Loading raw data")
    print("=" * 60)
    baci_raw          = load_baci(RAW_BACI_DIR, YEAR_START, YEAR_END)
    baci_countries, baci_products = load_baci_references(RAW_BACI_DIR)

    print("\n" + "=" * 60)
    print("STEP 2 — Filtering & cleaning BACI")
    print("=" * 60)
    algeria_exports, global_imports = clean_baci(baci_raw, ALGERIA_BACI_ID)

    print("\n" + "=" * 60)
    print("STEP 3 — HS code mapping")
    print("=" * 60)
    algeria_exports = add_hs_labels(algeria_exports, baci_products)

    print("\n" + "=" * 60)
    print("STEP 4 — Feature engineering")
    print("=" * 60)
    algeria_features = engineer_features(algeria_exports, global_imports)

    print("\n" + "=" * 60)
    print("STEP 5 — Loading & cleaning World Bank data")
    print("=" * 60)
    worldbank = load_worldbank(RAW_WB_DIR, WB_INDICATORS, YEAR_START, YEAR_END)

    print("\n" + "=" * 60)
    print("STEP 6 — Merging datasets")
    print("=" * 60)
    merged = merge_datasets(algeria_features, worldbank, baci_countries)

    print("\n" + "=" * 60)
    print("STEP 7 — Final cleaning & saving")
    print("=" * 60)
    final_df = final_clean_and_save(merged, PROCESSED_DIR)

    # Optional: global demand dataset for opportunity classification
    build_global_demand_dataset(
        global_imports, baci_products, worldbank, baci_countries,
        PROCESSED_DIR, YEAR_START, YEAR_END,
    )

    print_diagnostics(final_df)
    print("\nPreprocessing complete.")


if __name__ == "__main__":
    main()