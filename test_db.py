import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5433,
    dbname="mlproject",
    user="grafana",
    password="grafana123"
)

print("SUCCESS")
conn.close()