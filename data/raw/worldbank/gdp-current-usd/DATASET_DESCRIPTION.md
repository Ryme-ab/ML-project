# World Bank GDP (Current US$) Dataset Bundle

This folder contains a standard World Bank World Development Indicators export for the GDP (current US$) indicator.

## Files

- API_NY.GDP.MKTP.CD_DS2_en_csv_v2_133326.csv: main indicator panel with yearly values by country and aggregate.
- Metadata_Country_API_NY.GDP.MKTP.CD_DS2_en_csv_v2_133326.csv: country and aggregate metadata for the indicator export.
- Metadata_Indicator_API_NY.GDP.MKTP.CD_DS2_en_csv_v2_133326.csv: indicator definition and source metadata.

## Dataset Shape

- Indicator code: NY.GDP.MKTP.CD
- Indicator name: GDP (current US$)
- Source: World Development Indicators
- Last updated date: 2026-02-24

## Main Panel File Format

- Encoding: UTF-8 with BOM
- Header starts at line 5
- Structure: Country Name, Country Code, Indicator Name, Indicator Code, followed by yearly columns from 1960 to 2025
- Typical use: cross-country GDP level comparison and time-series analysis

## Metadata File Format

- Country metadata columns: Country Code, Region, IncomeGroup, SpecialNotes, TableName
- Indicator metadata columns: INDICATOR_CODE, INDICATOR_NAME, SOURCE_NOTE, SOURCE_ORGANIZATION

## Compatibility Notes

- The metadata country file is not a standalone panel; it only describes the rows in the main indicator CSV.
- Missing values in the panel file are represented as empty cells.
- The bundle includes both countries and aggregates, so downstream code should filter by Country Code or Region when needed.