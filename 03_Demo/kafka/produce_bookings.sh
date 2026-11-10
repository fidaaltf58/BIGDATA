#!/bin/sh
# ============================================================
#  KAFKA PRODUCER : simule l'arrivée de réservations en temps réel
#  (rejoue le dataset ligne par ligne, 5 réservations / seconde)
#    docker exec -it kafka sh /scripts/produce_bookings.sh [nb_lignes]
# ============================================================
N=${1:-300}
K=/opt/kafka/bin
$K/kafka-topics.sh --bootstrap-server kafka:9092 --create --if-not-exists \
  --topic hotel-bookings --partitions 3 --replication-factor 1
$K/kafka-topics.sh --bootstrap-server kafka:9092 --describe --topic hotel-bookings

echo ">>> Envoi de $N réservations sur le topic hotel-bookings ..."
tail -n +2 /data/hotel_bookings.csv | head -n "$N" | while IFS= read -r line; do
  echo "$line"
  sleep 0.2
done | $K/kafka-console-producer.sh --bootstrap-server kafka:9092 --topic hotel-bookings
echo ">>> Terminé."
