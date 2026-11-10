#!/bin/sh
# ============================================================
#  KAFKA CONSUMER : affiche les réservations reçues en temps réel
#    docker exec -it kafka sh /scripts/consume_bookings.sh
# ============================================================
/opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server kafka:9092 \
  --topic hotel-bookings \
  --group dashboard-live \
  --property print.partition=true \
  --property print.offset=true
