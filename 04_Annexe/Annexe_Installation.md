# Annexe : instructions d'installation et traces techniques

Projet Big Data (Hotel Booking Demand) : Kafka, Flume et Sqoop autour de HDFS

## 1. Vue d'ensemble de l'environnement

L'environnement de démonstration est conteneurisé avec Docker Compose. Il démarre 5 services :

- namenode : maître HDFS (Hadoop 3.2.1), interface web sur http://localhost:9870
- datanode : stockage des blocs HDFS
- mysql : MySQL 8.0, qui joue le rôle du PMS de l'hôtel (base hotel_db, table bookings chargée automatiquement)
- kafka : Apache Kafka 3.7.0 en mode KRaft (sans ZooKeeper), port interne 9092 et port externe 29092
- tools : client Hadoop + Apache Flume 1.11.0 + Apache Sqoop 1.4.7 (image construite depuis 03_Demo/tools/Dockerfile)

Arborescence du livrable :

```
BIG DATA/
├── 01_Presentation/   Projet_BigData_Hotel_MiParcours.pptx (+ build_deck.py)
├── 02_Dataset/        hotel_bookings.csv, web_access.log, kpi_monthly.csv, prepare_kpi.py
├── 03_Demo/           docker-compose.yml, tools/Dockerfile, flume/, kafka/, mysql/, scripts/
└── 04_Annexe/         ce document + captures/ (captures d'écran à ajouter)
```

## 2. Prérequis sous Windows

1. Ouvrir PowerShell en administrateur et installer WSL 2 :

```
wsl --install
```

2. Redémarrer le PC.
3. Installer Docker Desktop (https://www.docker.com/products/docker-desktop), en cochant « Use WSL 2 based engine ».
4. Dans Docker Desktop > Settings > Resources, allouer au moins 6 Go de RAM.
5. Vérifier l'installation :

```
docker version
docker compose version
```

## 3. Démarrage de la stack

```
cd "C:\Users\<vous>\Desktop\CIC\BIG DATA\03_Demo"
docker compose up -d --build
docker compose ps
```

Le premier lancement télécharge les images (environ 2 Go) et construit l'image tools. Comptez 5 à 10 minutes.

Vérifications :

- HDFS : ouvrir http://localhost:9870 ; la page Datanodes doit afficher 1 nœud actif.
- MySQL : `docker exec -it mysql mysql -usqoop -psqoop hotel_db -e "SELECT COUNT(*) FROM bookings;"` doit renvoyer 119390.
- Kafka : `docker exec -it kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka:9092 --list`
- Outils : `docker exec -it tools bash -c "sqoop version; flume-ng version"`

## 4. Apache Sqoop : import et export SGBDR ↔ HDFS

### 4.1 Installation (réalisée dans le Dockerfile)

1. Télécharger sqoop-1.4.7.bin__hadoop-2.6.0.tar.gz depuis archive.apache.org et le décompresser dans /opt/sqoop.
2. Copier le driver JDBC mysql-connector-j-8.0.33.jar dans /opt/sqoop/lib.
3. Ajouter commons-lang-2.6.jar dans /opt/sqoop/lib : Sqoop 1.4.7 est compilé pour Hadoop 2 et ce jar manque avec Hadoop 3.
4. Créer conf/sqoop-env.sh avec HADOOP_COMMON_HOME et HADOOP_MAPRED_HOME.
5. Ajouter /opt/sqoop/bin au PATH.

### 4.2 Utilisation

```
docker exec -it tools bash /scripts/01_sqoop_import.sh
```

Commande principale :

```
sqoop import --connect "jdbc:mysql://mysql:3306/hotel_db?useSSL=false&allowPublicKeyRetrieval=true" \
  --username sqoop --password sqoop --table bookings \
  --target-dir /data/hotel/bookings --split-by booking_id --num-mappers 4 --fields-terminated-by ','
```

Résultat attendu : 4 fichiers part-m-0000X dans /data/hotel/bookings, soit 119 390 lignes au total.

Export des KPI (HDFS vers MySQL) :

```
docker exec -it tools bash /scripts/04_sqoop_export.sh
```

## 5. Apache Flume : ingestion des logs web

### 5.1 Installation (réalisée dans le Dockerfile)

1. Télécharger apache-flume-1.11.0-bin.tar.gz et le décompresser dans /opt/flume.
2. Supprimer lib/guava-*.jar de Flume : l'ancienne version de Guava provoque un NoSuchMethodError avec le client HDFS de Hadoop 3.
3. Vérifier que la commande hadoop est dans le PATH, afin que flume-ng ajoute automatiquement le classpath Hadoop.

### 5.2 Configuration de l'agent (03_Demo/flume/weblogs-hdfs.conf)

- Source spooldir sur /var/spool/weblogs, avec un intercepteur timestamp
- Channel file, durable
- Sink HDFS vers /data/hotel/weblogs/dt=%Y-%m-%d, avec un roulement de fichier toutes les 30 s

### 5.3 Utilisation

Terminal 1 (agent Flume) :

```
docker exec -it tools bash /scripts/02_flume_weblogs.sh
```

Terminal 2 (génération de logs en continu depuis Windows) :

```
python 03_Demo\scripts\generate_weblogs.py --live
```

Vérification :

```
docker exec -it tools hdfs dfs -ls -R /data/hotel/weblogs
```

Les fichiers ingérés sont renommés *.COMPLETED dans le dossier 03_Demo/spool.

## 6. Apache Kafka : flux temps réel des réservations

### 6.1 Installation manuelle (hors Docker)

1. Télécharger kafka_2.13-3.7.0.tgz depuis kafka.apache.org et le décompresser.
2. Générer un identifiant de cluster et formater le stockage :

```
KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"
bin/kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c config/kraft/server.properties
```

3. Démarrer le broker :

```
bin/kafka-server-start.sh config/kraft/server.properties
```

Dans Docker, l'image officielle apache/kafka:3.7.0 effectue ces étapes à partir des variables d'environnement définies dans docker-compose.yml.

### 6.2 Utilisation

Terminal 1 (consommateur console) :

```
docker exec -it kafka sh /scripts/consume_bookings.sh
```

Terminal 2 (consommateur d'alertes Python sous Windows) :

```
pip install kafka-python-ng
python 03_Demo\scripts\kafka_alerts_consumer.py
```

Terminal 3 (producteur, 300 réservations à 5 par seconde) :

```
docker exec -it kafka sh /scripts/produce_bookings.sh 300
```

Archivage du flux dans HDFS par Flume (source Kafka) :

```
docker exec -it tools bash /scripts/03_flume_kafka_archive.sh
```

## 7. Alternative : machine virtuelle Cloudera

L'enseignant accepte aussi une VM contenant les trois outils. Avec la Cloudera QuickStart VM (CDH 5.x) :

- Sqoop et Flume sont préinstallés : les mêmes commandes s'appliquent, en remplaçant mysql par localhost (MySQL est inclus dans la VM, utilisateur root / cloudera).
- Kafka n'est pas inclus par défaut : il faut l'ajouter via Cloudera Manager (parcel Kafka) ou installer l'archive Apache Kafka manuellement comme au §6.1.
- La VM demande au moins 8 Go de RAM et VirtualBox ou VMware.

## 8. Problèmes connus et corrections appliquées

| Problème | Cause | Correction |
|---|---|---|
| Flume → HDFS : java.lang.NoSuchMethodError (com.google.common.base.Preconditions) | Flume embarque une vieille Guava, Hadoop 3 attend Guava 27 | Suppression de lib/guava-*.jar de Flume |
| Sqoop : NoClassDefFoundError org/apache/commons/lang/StringUtils | Sqoop 1.4.7 compilé pour Hadoop 2 | Ajout de commons-lang-2.6.jar dans sqoop/lib |
| Sqoop : Public Key Retrieval is not allowed | Authentification caching_sha2_password de MySQL 8 | allowPublicKeyRetrieval=true dans l'URL JDBC, mysql_native_password |
| Client Kafka Windows : connexion impossible | advertised.listeners annonçait kafka:9092, inconnu de Windows | Listener EXTERNAL annoncé sur localhost:29092 |
| Chargement CSV : valeurs « NA » | Colonne children non numérique | NULLIF(@children,'NA') dans LOAD DATA |
| Sqoop : job MapReduce bloqué en attente de YARN | Pas de ResourceManager dans la stack | mapreduce.framework.name=local |

## 9. Traces à joindre (à compléter par le groupe)

Placer les captures dans 04_Annexe/captures/ en les nommant ainsi :

1. 01_docker_compose_ps.png : les 5 conteneurs « running »
2. 02_hdfs_ui_datanodes.png : l'interface http://localhost:9870
3. 03_sqoop_import_ok.png : fin du job (« Retrieved 119390 records »)
4. 04_hdfs_bookings.png : contenu de /data/hotel/bookings
5. 05_flume_agent.png : l'agent en cours d'exécution et les fichiers dans /data/hotel/weblogs
6. 06_kafka_producer_consumer.png : le producteur et le consommateur côte à côte
7. 07_kafka_alertes.png : les alertes du consommateur Python
8. 08_sqoop_export_mysql.png : le résultat du SELECT sur kpi_monthly
9. Les captures de toutes les erreurs rencontrées, même résolues

Pour enregistrer les logs complets d'une commande :

```
docker exec tools bash /scripts/01_sqoop_import.sh > 04_Annexe\logs\sqoop_import.log 2>&1
```
