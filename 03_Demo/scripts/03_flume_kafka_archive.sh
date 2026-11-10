#!/bin/bash
# ============================================================
#  FLUME (source Kafka) : archive le flux temps réel dans HDFS
#    docker exec -it tools bash /scripts/03_flume_kafka_archive.sh
# ============================================================
hdfs dfs -mkdir -p /data/hotel/stream
echo "=== Agent Flume 'stream' : topic hotel-bookings -> HDFS /data/hotel/stream ==="
flume-ng agent \
  --name stream \
  --conf $FLUME_HOME/conf \
  --conf-file /opt/flume-conf/kafka-hdfs.conf \
  -Dflume.root.logger=INFO,console
