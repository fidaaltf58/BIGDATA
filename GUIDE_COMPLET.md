# Complete guide: Big Data midterm evaluation

## 1. What the professor wants

Format:

- A midterm check on the Big Data project, done in groups of up to 3.
- Each group gets 10 to 15 minutes. All members must be present on time; more than 15 minutes late counts as absent.
- This is a rehearsal. The final evaluation happens at the last class session, probably after the holidays.

The four expected deliverables:

| # | The professor asked for | What we have | File |
|---|---|---|---|
| a | The problem and the chosen case study | Hotels: anticipating cancellations | Slides 1 to 7 |
| b | A dataset that fits the domain | Hotel Booking Demand (Kaggle), 119,390 bookings | `02_Dataset/` and slides 8 to 9 |
| c | A technical demo of Kafka, Flume and Sqoop installed and working (Cloudera or another VM is accepted) | A Docker stack with the 3 tools connected to HDFS | `03_Demo/` and slide 14 |
| d | Any technical trace of your installation effort, even if it failed (instruction file, screenshots of errors) | Installation annex, automatic logs, screenshots | `04_Annexe/` and slide 15 |

From the project PDF, the PowerPoint must cover:

1. The 4 general questions: why Big Data, at what level, how it was used, and the steps. These are slides 3 to 6.
2. The 3 tools, with their role, installation and usage. These are slides 11 to 13.
3. The use case. This is slides 7 to 10.

Also required: a demo of the 3 tools, and an annex with the installation instructions.

## 2. Our project in 30 seconds

> "Hotels lose a lot of money to cancellations: 37% of bookings in our dataset, or €16.7M. We built a Big Data architecture that brings together the hotel's bookings (MySQL, imported with **Sqoop**), its website logs (collected by **Flume**) and new bookings in real time (streamed by **Kafka**) in an **HDFS** Data Lake. A Kafka consumer flags risky bookings live, and the monthly KPIs are sent back to MySQL with **Sqoop export**."

## 3. The 3 tools, to know by heart

### Kafka: real time

- What it is: a distributed streaming platform. *Producers* write messages to *topics*, which are split into *partitions*, and *consumers* read them.
- Why we use it: bookings arrive continuously. Kafka keeps the messages, so several consumers can read the same stream independently. In our project, those consumers are the alerts, the console and the Flume archive.
- In our project: the topic `hotel-bookings` has 3 partitions. The producer replays the CSV at 5 bookings per second, and a Python consumer computes a cancellation-risk score.
- KRaft mode: Kafka without ZooKeeper (the default since Kafka 3.3; ZooKeeper is removed in Kafka 4).

### Flume: log files

- What it is: a log collection service. An *agent* is made of a **Source**, a **Channel** and a **Sink**, configured in a `.conf` file.
- Why we use it: the booking website produces log files nonstop, and Flume moves them to HDFS automatically.
- In our project: a `spooldir` source (watches a folder), a `file` channel (durable, so nothing is lost if the agent restarts) and an `hdfs` sink partitioned by date. A second agent reads from Kafka and archives the stream in HDFS.

### Sqoop: SQL database ↔ HDFS

- What it is: a bulk transfer tool between relational databases and Hadoop. It generates parallel MapReduce jobs.
- Why we use it: the hotel's historical bookings live in a MySQL database (the PMS).
- In our project: `import` of the `bookings` table into HDFS (4 mappers, `--split-by booking_id`), a filtered import (`--where`), and `export` of the KPIs to the MySQL table `kpi_monthly`.
- Incremental import: `--incremental append --check-column booking_id --last-value N`.

### HDFS

The distributed file system where all the data is centralized (the Data Lake). Its web interface is at http://localhost:9870.

## 4. Installation: what to do on your PC

> **Docker and WSL are NOT installed on this PC yet.** Do this at least 2 days before the evaluation.

Step 0, done once (about 20 minutes, includes a reboot):

1. Right-click PowerShell, choose **Run as administrator**, then run:

   ```
   Set-ExecutionPolicy -Scope Process Bypass -Force
   & "C:\Users\Fidal\Desktop\CIC\BIG DATA\03_Demo\00_INSTALL_Docker.ps1"
   ```

2. **Reboot** the PC.
3. Launch **Docker Desktop**, accept the terms, and wait until it shows "Engine running".

Step 1, the full automatic test (about 15 minutes the first time). In a normal PowerShell window, run:

```
Set-ExecutionPolicy -Scope Process Bypass -Force
& "C:\Users\Fidal\Desktop\CIC\BIG DATA\03_Demo\01_RUN_DEMO.ps1"
```

This script starts all 5 containers, then tests Sqoop import, Kafka, Flume (logs, and Kafka to HDFS) and Sqoop export. Every step is saved to `04_Annexe/logs/`, and those logs are your technical traces (deliverable d).

Step 2, screenshots. Take the 8 screenshots listed in `04_Annexe/Annexe_Installation.docx`, section 9, plus **every error you get**. The professor explicitly values traces of failures.

If something fails, copy the error and send it to me. Even a failure that ends up fixed becomes a trace for slide 15.

Plan B: the Cloudera QuickStart VM is accepted by the professor (see annex section 7).

## 5. Final checklist

- [ ] Docker installed and `01_RUN_DEMO.ps1` run successfully at least once
- [ ] Group names entered on slide 1
- [ ] Slide 15 adapted to the errors you actually hit
- [ ] Screenshots in `04_Annexe/captures/`
- [ ] Each member has rehearsed their part (`03_Demo/DEMO_SCRIPT.md`)
- [ ] On the day: stack started 15 minutes before (`docker compose up -d` in `03_Demo`), PC charged, terminals ready
- [ ] Bring the whole folder on a USB stick, and have the screenshots ready if the live demo fails

## 6. Questions the professor might ask

| Question | Short answer |
|---|---|
| Why Kafka AND Flume? | Kafka handles the real-time stream with multiple consumers and replay. Flume moves files and logs into HDFS. They complement each other, and Flume can even read from Kafka. |
| Memory channel vs file channel? | Memory is fast but loses data if the agent crashes. File is durable. |
| What is `--split-by` for? | It spreads the import across the mappers using a numeric column. |
| What is `-m 1`? | A single mapper, needed when there is no primary key. |
| What is a Kafka partition? | A unit of parallelism. Messages are ordered within a partition, and consumers in a group share the partitions between them. |
| What is an offset? | The position of a message in a partition. It lets a consumer resume where it stopped. |
| Why HDFS rather than MySQL for everything? | Low-cost storage that scales horizontally, for all formats (logs, CSV, JSON), with fault tolerance through replication. |
| What's next? | Hive and Spark processing, a cancellation-prediction model and a dashboard, for the final evaluation. |
| Why 99% cancellations on "Non Refund"? | A known anomaly in the dataset, which we'll study in the analysis phase. |
