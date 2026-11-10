#!/bin/bash
# ============================================================
#  SQOOP IMPORT : MySQL (hotel_db.bookings) -> HDFS
#  Exécuté dans le conteneur "tools" :
#    docker exec -it tools bash /scripts/01_sqoop_import.sh
# ============================================================
set -e
JDBC="jdbc:mysql://mysql:3306/hotel_db?useSSL=false&allowPublicKeyRetrieval=true"

echo "=== 1. Lister les bases et tables visibles par Sqoop ==="
sqoop list-databases --connect "jdbc:mysql://mysql:3306/?useSSL=false&allowPublicKeyRetrieval=true" \
  --username sqoop --password sqoop
sqoop list-tables --connect "$JDBC" --username sqoop --password sqoop

echo "=== 2. Import complet de la table bookings vers HDFS (4 mappers, découpage sur la clé) ==="
hdfs dfs -rm -r -f /data/hotel/bookings
sqoop import \
  --connect "$JDBC" --username sqoop --password sqoop \
  --table bookings \
  --target-dir /data/hotel/bookings \
  --split-by booking_id \
  --num-mappers 4 \
  --fields-terminated-by ',' \
  --null-string '' --null-non-string ''

echo "=== 3. Import incrémental (seulement les nouvelles réservations) ==="
echo "    exemple : sqoop import ... --incremental append --check-column booking_id --last-value 119390"

echo "=== 4. Import filtré : réservations annulées du Resort Hotel ==="
hdfs dfs -rm -r -f /data/hotel/canceled_resort
sqoop import \
  --connect "$JDBC" --username sqoop --password sqoop \
  --table bookings \
  --where "is_canceled = 1 AND hotel = 'Resort Hotel'" \
  --columns "booking_id,hotel,lead_time,deposit_type,adr,country" \
  --target-dir /data/hotel/canceled_resort \
  -m 1

echo "=== Résultat dans HDFS ==="
hdfs dfs -ls /data/hotel/bookings
hdfs dfs -cat /data/hotel/bookings/part-m-00000 | head -5
echo "Nombre de lignes importées :"
hdfs dfs -cat /data/hotel/bookings/part-m-* | wc -l
