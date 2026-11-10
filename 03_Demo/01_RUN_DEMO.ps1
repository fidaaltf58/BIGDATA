# ============================================================
#  ÉTAPE 1 : démarre la stack et teste les 3 outils de bout en bout.
#  Chaque étape est enregistrée dans 04_Annexe\logs (= traces techniques).
#    Set-ExecutionPolicy -Scope Process Bypass -Force
#    & "C:\Users\Fidal\Desktop\CIC\BIG DATA\03_Demo\01_RUN_DEMO.ps1"
# ============================================================
$ErrorActionPreference = "Continue"
$demo = $PSScriptRoot
$logs = Join-Path (Split-Path $demo -Parent) "04_Annexe\logs"
New-Item -ItemType Directory -Force $logs | Out-Null
Set-Location $demo

function Step($name, $file, [scriptblock]$cmd) {
    Write-Host "`n===== $name =====" -ForegroundColor Cyan
    $path = Join-Path $logs $file
    & $cmd 2>&1 | ForEach-Object { "$_" } | Tee-Object -FilePath $path
    Write-Host "-> trace enregistrée : $path" -ForegroundColor DarkGray
}

Step "Versions" "00_versions.log" { docker version; docker compose version }
Step "Construction + démarrage de la stack (5-10 min la 1re fois)" "01_docker_compose_up.log" { docker compose up -d --build }

Write-Host "`nAttente de MySQL (chargement des 119 390 lignes)..." -ForegroundColor Yellow
for ($i = 0; $i -lt 60; $i++) {
    $n = docker exec mysql mysql -usqoop -psqoop -N -e "SELECT COUNT(*) FROM hotel_db.bookings" 2>$null
    if ($n -match "^\d+$" -and [int]$n -gt 0) { Write-Host "MySQL prêt : $n lignes"; break }
    Start-Sleep 5
}
Write-Host "Attente de HDFS (sortie du safe mode)..." -ForegroundColor Yellow
docker exec namenode hdfs dfsadmin -safemode wait

Step "État des conteneurs" "02_docker_ps.log" { docker compose ps }
Step "Versions des outils" "03_tools_versions.log" {
    docker exec tools bash -c "hadoop version | head -1; sqoop version 2>/dev/null | grep Sqoop; flume-ng version | head -1"
    docker exec kafka /opt/kafka/bin/kafka-topics.sh --version
}
Step "SQOOP IMPORT  MySQL -> HDFS" "04_sqoop_import.log" { docker exec tools bash /scripts/01_sqoop_import.sh }

Step "KAFKA  producteur (100 réservations)" "05_kafka_producer.log" { docker exec kafka sh /scripts/produce_bookings.sh 100 }
Step "KAFKA  lecture du topic (10 premiers messages)" "06_kafka_consumer.log" {
    docker exec kafka /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server kafka:9092 `
        --topic hotel-bookings --from-beginning --max-messages 10 --property print.partition=true
}

Step "FLUME  logs web -> HDFS (agent lancé 60 s)" "07_flume_weblogs.log" {
    docker exec tools bash -c "cp /data/web_access.log /var/spool/weblogs/web_access_sample.log 2>/dev/null; mkdir -p /tmp/flume/weblogs; timeout 60 flume-ng agent -n weblogs -c `$FLUME_HOME/conf -f /opt/flume-conf/weblogs-hdfs.conf -Dflume.root.logger=INFO,console; hdfs dfs -ls -R /data/hotel/weblogs"
}
Step "FLUME  Kafka -> HDFS (agent lancé 45 s)" "08_flume_kafka.log" {
    docker exec tools bash -c "timeout 45 flume-ng agent -n stream -c `$FLUME_HOME/conf -f /opt/flume-conf/kafka-hdfs.conf -Dflume.root.logger=INFO,console; hdfs dfs -ls -R /data/hotel/stream"
}
Step "SQOOP EXPORT  HDFS -> MySQL" "09_sqoop_export.log" { docker exec tools bash /scripts/04_sqoop_export.sh }
Step "Contenu final du Data Lake" "10_hdfs_final.log" { docker exec namenode hdfs dfs -du -h /data/hotel }

Write-Host "`nTERMINÉ. Ouvrez http://localhost:9870 > Utilities > Browse the file system > /data/hotel" -ForegroundColor Green
Write-Host "Traces dans : $logs  (faites aussi vos captures d'écran dans 04_Annexe\captures)" -ForegroundColor Green
