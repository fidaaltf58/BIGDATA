# Déroulé de l'évaluation (10 à 15 min)

## Avant la séance (le matin même)

- [ ] `cd 03_Demo` puis `docker compose up -d`, attendre 2 min, puis `docker compose ps` : 5 conteneurs « running »
- [ ] Vérifier que http://localhost:9870 s'ouvre
- [ ] Lancer une fois `01_sqoop_import.sh`, pour que HDFS contienne déjà des données si la démo live échoue
- [ ] Ouvrir 4 onglets dans Windows Terminal (voir ci-dessous), police agrandie
- [ ] Ouvrir le PowerPoint et le dossier 04_Annexe/captures (plan B)

## Répartition (groupe de 3)

| Temps | Qui | Contenu |
|---|---|---|
| 0:00 à 4:00 | Membre 1 | Slides 1 à 6 : partie générale (pourquoi, à quel niveau, comment, étapes) |
| 4:00 à 7:00 | Membre 2 | Slides 7 à 13 : problématique, dataset, constats, architecture, les 3 outils |
| 7:00 à 11:00 | Membre 3 | Slide 14 : démo live |
| 11:00 à 12:00 | Membre 2 | Slide 15 : traces et difficultés, puis slide 16 : conclusion |
| 12:00 à 15:00 | Tous | Questions |

## Démo live (4 min)

Onglet 1 : Sqoop (1 min)

```
docker exec -it tools bash /scripts/01_sqoop_import.sh
```

À dire : « Sqoop lance 4 mappers en parallèle, découpés sur booking_id. » Ensuite, montrer /data/hotel/bookings dans l'interface HDFS.

Onglet 2 : Flume (1 min)

```
docker exec -it tools bash /scripts/02_flume_weblogs.sh
```

Onglet 3 (Windows) : `python scripts\generate_weblogs.py --live`. Montrer les fichiers renommés .COMPLETED dans spool, puis /data/hotel/weblogs dans HDFS.

Onglet 4 : Kafka (1 min 30)

Ouvrir côte à côte :

```
python scripts\kafka_alerts_consumer.py
docker exec -it kafka sh /scripts/produce_bookings.sh 200
```

À dire : « Chaque réservation est publiée sur le topic ; le consommateur calcule un score de risque d'annulation en temps réel. »

Sqoop export (30 s)

```
docker exec -it tools bash /scripts/04_sqoop_export.sh
```

Montrer le tableau final affiché par sqoop eval.

## Questions probables

- Pourquoi Kafka plutôt que Flume pour le temps réel ? Kafka conserve les messages et permet plusieurs consommateurs indépendants qui peuvent rejouer le flux. Flume est un pipeline de collecte vers un puits.
- Pourquoi un channel file plutôt que memory ? Pour la durabilité : aucun événement n'est perdu si l'agent redémarre.
- À quoi sert --split-by ? À répartir l'import entre les mappers selon une colonne numérique ; la clé primaire garantit une répartition homogène.
- Différence entre import incrémental append et lastmodified ? append sert aux nouvelles lignes (ID croissant), lastmodified aux lignes mises à jour (colonne date).
- Pourquoi 99 % d'annulations sur « Non Refund » ? C'est une anomalie connue du dataset, probablement liée à des réservations de groupes ou d'agences ; nous l'étudierons dans la phase d'analyse.
- Pourquoi pas de ZooKeeper ? Depuis Kafka 3.3, le mode KRaft est prêt pour la production, et ZooKeeper est supprimé dans Kafka 4.
