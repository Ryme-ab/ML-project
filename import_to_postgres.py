import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path

folder = Path(r"C:\Users\DELL\ML-project\algerian-export-ml\data\processed")


engine = create_engine(
    "postgresql+psycopg2://grafana:grafana123@localhost:5433/mlproject"
)
for file in folder.glob("*.csv"):
    print(f"Loading {file.name}")

    df = pd.read_csv(file)

    table_name = (
        file.stem
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    df.to_sql(
        table_name,
        engine,
        if_exists="replace",
        index=False
    )

print("Import finished successfully")