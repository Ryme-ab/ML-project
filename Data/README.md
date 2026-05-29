# Global Bilateral Trade Dataset (BACI HS92 - V202601) with Focus on Algeria (1995–2024)

###  Context & Dataset Overview
This dataset provides a cleaned, high-performance compilation of global international trade data spanning **30 years (1995–2024)**. It is built entirely from the **BACI HS92 V202601** release published by **CEPII**, which represents the gold standard in trade econometrics. 

BACI reconciles raw bilateral trade flows reported to the United Nations Comtrade database by matching and correcting discrepancies between what exporting countries say they shipped and what importing countries report receiving (mirror statistics). 

While this clean panel contains the entire matrix of global demand across **5,018 distinct products**, it features localized ISO codes specifically tailored for analyzing **Algeria's export architecture (ISO3: DZA)**, making it ideal for economic diversification research and advanced machine learning time-series forecasting.

---


##  Dataset Repository & Live Access
The official dataset, optimized Parquet files, and benchmark scripts are hosted and maintained on Kaggle:
 **[Global Bilateral Trade Dataset (BACI HS92) - Focus on Algeria](https://www.kaggle.com/datasets/ayastudentbrahimi/algeria-exports-1995-2024)**

---

##  Data Pipeline & Manifest Details
* **Source Release:** CEPII BACI HS92 V202601
* **Input Structure:** Compiled from 30 raw annual CSV files and combined with official country code lookups.
* **Output Format:** Optimized Apache `baci_clean.parquet` 
* **File Size:** ~1.97 GB
* **Data Integrity (SHA-256 Hash):** `63148a49a404464726d8997e97cc694b08ec786a95ffc5359446d465b94dc8c8`
* **Pipeline Processing Time:** 1,007.43 seconds (~16.7 minutes)

---

##  Dataset Scale & Summary Statistics
The dataset is an exhaustive matrix containing **269,894,500 rows** distributed over three decades:
* **Temporal Range:** 1995 – 2024 (30 continuous years)
* **Global Footprint:** 231 Exporters | 232 Importers
* **Product Granularity:** 5,018 unique product lines classified at the 6-digit Harmonised System level (HS6).

---

##  Data Schema
The dataset is structured as a flat, highly compressed tabular panel containing the following features:

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| **Year** | `int64` | The calendar year of the trade transaction (1995–2024). |
| **Exporter** | `int64` | CEPII numeric country code for the exporting nation. |
| **Importer** | `int64` | CEPII numeric country code for the importing nation. |
| **Exporter_ISO3**| `string` | Standardized 3-character ISO country code of the exporter (e.g., `DZA` for Algeria). |
| **Importer_ISO3**| `string` | Standardized 3-character ISO country code of the importer. |
| **Product** | `string` | Zero-padded 6-digit Harmonised System (HS6) product code. |
| **Value** | `float64` | Value of the trade flow in **Thousands of USD** ($ USD > 0). |
| **Quantity** | `float64` | Total weight of the shipment in **Metric Tons** (Nullable). |

---

## 📈 Reference Data: Algeria's Historical Export Totals
For validation and benchmarking, the total historical export values for Algeria extracted from this dataset (in thousands of USD) are as follows:

* **1995:** $11,251,762  
* **2000:** $24,179,594  
* **2005:** $48,426,899  
* **2008 (Oil Peak):** $84,306,435  
* **2015 (Oil Crash):** $39,317,205  
* **2020 (Pandemic Low):** $21,983,214  
* **2022 (Recovery Peak):** $64,851,135  
* **2024 (Latest Actuals):** $48,158,721  

---

##  Potential Use Cases
1. **Time-Series Forecasting:** Train panel models (AutoARIMA, Prophet, or Deep Learning like Temporal Fusion Transformers) to predict global demand patterns.
2. **Economic Diversification Analysis:** Study Algeria's non-hydrocarbon sector development (e.g., Fertilizers, Inorganic Chemicals, Cement Clinker) relative to global shifting markets.
3. **Network Analysis & Gravity Modeling:** Map the spatial graph network of international trade links and calculate country dependencies over time.

---
