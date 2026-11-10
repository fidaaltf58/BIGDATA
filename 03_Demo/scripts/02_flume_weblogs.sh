#!/bin/bash
# ============================================================
#  FLUME : ingestion des logs web du moteur de réservation -> HDFS
#    docker exec -it tools bash /scripts/02_flume_weblogs.sh
#  (Pendant ce temps, déposer des fichiers .log dans 03_Demo/spool,
#   ex. :  python 03_Demo/scripts/generate_weblogs.py --live)
# ============================================================
mkdir -p /tmp/flume/weblogs
hdfs dfs -mkdir -p /data/hotel/weblogs

# Dépôt d'un premier fichier de logs (échantillon du dataset)
if [ -f /data/web_access.log ] && [ ! -f /var/spool/weblogs/web_access_sample.log.COMPLETED ]; then
  cp /data/web_access.log /var/spool/weblogs/web_access_sample.log
fi

echo "=== Démarrage de l'agent Flume 'weblogs' (Ctrl+C pour arrêter) ==="
echo "    Vérifier ensuite :  hdfs dfs -ls -R /data/hotel/weblogs"
flume-ng agent \
  --name weblogs \
  --conf $FLUME_HOME/conf \
  --conf-file /opt/flume-conf/weblogs-hdfs.conf \
  -Dflume.root.logger=INFO,console
