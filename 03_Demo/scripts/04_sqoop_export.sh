#!/bin/bash
# ============================================================
#  SQOOP EXPORT : KPI mensuels calculés (HDFS) -> MySQL kpi_monthly
#  Les KPI (02_Dataset/kpi_monthly.csv) représentent la sortie de la
#  couche de traitement (Hive/Spark en phase finale du projet).
#    docker exec -it tools bash /scripts/04_sqoop_export.sh
# ============================================================
set -e
JDBC="jdbc:mysql://mysql:3306/hotel_db?useSSL=false&allowPublicKeyRetrieval=true"

echo "=== 1. Dépôt des KPI dans HDFS ==="
hdfs dfs -mkdir -p /data/hotel/kpi
tail -n +2 /data/kpi_monthly.csv > /tmp/kpi_monthly_noheader.csv
hdfs dfs -put -f /tmp/kpi_monthly_noheader.csv /data/hotel/kpi/kpi_monthly.csv
hdfs dfs -cat /data/hotel/kpi/kpi_monthly.csv | head -5

echo "=== 2. Export Sqoop vers MySQL ==="
sqoop eval --connect "$JDBC" --username sqoop --password sqoop --query "TRUNCATE TABLE kpi_monthly"
sqoop export \
  --connect "$JDBC" --username sqoop --password sqoop \
  --table kpi_monthly \
  --export-dir /data/hotel/kpi \
  --input-fields-terminated-by ',' \
  -m 1

echo "=== 3. Vérification côté MySQL ==="
sqoop eval --connect "$JDBC" --username sqoop --password sqoop \
  --query "SELECT hotel, year_month_key, total_bookings, cancel_rate_pct, avg_adr FROM kpi_monthly ORDER BY cancel_rate_pct DESC LIMIT 10"
