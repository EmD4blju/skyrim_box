# Skyrim Box: Big Data Pipeline Summary (Phases 3 - 5)

This document serves as a comprehensive recap of the Big Data Data Engineering pipeline constructed for the **Skyrim Box** project. It details how the transactional database seamlessly integrates with a real-time analytics Data Lake.

---

## 🏗️ Architecture Overview

The pipeline implements a **Change Data Capture (CDC) Architecture**, effectively decoupling our transactional app (FastAPI + Postgres) from our analytical storage (MinIO). 

**The Data Flow:**  
`PostgreSQL (WAL)` ➡️ `Debezium` ➡️ `Apache Kafka` ➡️ `Apache Spark (Structured Streaming)` ➡️ `MinIO (Data Lake / Parquet)`

All services operate within a unified `docker-compose.yml` network. By sharing this default Docker network, containers resolve and talk to each other using their container names as hostnames (e.g., `postgres`, `kafka`, `minio`).

---

## 🛠️ Phase 3: Infrastructure Setup

We orchestrated a 7-container microservice cluster using `docker-compose.yml`. Here is how they interact:

1. **PostgreSQL** (`skyrim_postgres`):
   * **Role:** The transactional database. 
   * **Configuration:** We started it with the command `-c wal_level=logical`. This is critical—it tells Postgres to keep a detailed "Write-Ahead Log" (WAL) of every single row change (INSERT, UPDATE, DELETE) rather than just crash-recovery logs.
2. **Confluent Zookeeper** (`skyrim_zookeeper`):
   * **Role:** Cluster metadata manager for Kafka. It coordinates broker availability and elects partition leaders.
3. **Confluent Kafka** (`skyrim_kafka`):
   * **Role:** A high-throughput, distributed message broker.
   * **Connection Detail:** It uses `ADVERTISED_LISTENERS`. It listens internally for Debezium/Spark on `kafka:29092`, and externally for your host machine on `localhost:9092`.
4. **Debezium** (`skyrim_debezium`):
   * **Role:** The CDC engine. It observes the Postgres WAL and pushes events to Kafka.
   * **Connection Detail:** It connects directly to the `kafka` container and is managed via an HTTP Rest API on port `8083`.
5. **Apache Spark Cluster** (`spark-master` & `spark-worker`):
   * **Role:** The distributed compute engine that transforms and routes our data streams. 
   * **Connection Detail:** The worker connects directly to the master via `spark://spark-master:7077`.
6. **MinIO** (`skyrim_minio`):
   * **Role:** An S3-compatible local object-storage server serving as our Data Lake. It hosts our `skyrim-lake` bucket.

---

## 📡 Phase 4: CDC & Streaming (Debezium + Kafka)

**Goal:** Automatically stream every database change into Kafka almost instantly, without burdening the FastAPI backend with dual-writing logic.

**How we built it:**
1. We wrote `setup_debezium.py` to send a JSON configuration payload (via POST request) to the Debezium container's REST API (`http://localhost:8083/connectors`).
2. **The Plugin:** We configured Debezium to use the `pgoutput` plugin. This is Postgres's native logical decoding plugin. Debezium acts like a "replica" database, constantly reading the WAL.
3. **Table Filtering:** In the config, we specified `"table.include.list": "public.user,public.item,public.comment"`. This ensures we don't stream irrelevant system tables.
4. **Topic Generation:** Once registered, Debezium took an initial "snapshot" of the existing Postgres tables and pushed them to Kafka. Every table gets its own topic, named with a prefix we defined: `skyrim.public.user`, `skyrim.public.item`, and `skyrim.public.comment`.

Every time a user posts a comment on the React frontend, Postgres writes to its WAL, Debezium instantly reads it, and turns it into a JSON message (containing the `before` and `after` state of the row) placed tightly into the Kafka topic.

---

## 🌊 Phase 5: The Data Lake (Spark + MinIO)

**Goal:** Consume the rapid stream of messages from Kafka and permanently store them in a persistent, query-friendly Data Lake directory.

**How we built it:**
1. **The PySpark Script** (`stream_to_data_lake.py`): We used Spark's "Structured Streaming" API to define an endless, constantly running job.
2. **Authentication:** Spark was configured with S3 AWS credentials (access key: `minioadmin`, secret: `minioadmin123`) and aimed at the MinIO container's API endpoint (`http://minio:9000`).
3. **Consuming from Kafka:** The script connects to `kafka:29092`, subscribing to the pattern `skyrim.public.*`. It reads the raw binary JSON payload that Debezium created.
4. **Transformation:** The payload is cast from binary to standard String format in memory.
5. **Writing to MinIO:**
   * `format("parquet")`: We instructed Spark to write the data out in **Parquet** format. Parquet is a columnar binary file format crucial for Big Data. It provides massive compression and ultra-fast column lookups compared to raw JSON or CSV.
   * `partitionBy("topic")`: Spark reads streams from multiple topics simultaneously. This command tells Spark to dynamically create sub-folders in MinIO based on the table name.
   * **Checkpoints:** Spark maintains a exact state of what Kafka offset it has read inside the `checkpoints/` folder. If the Spark container crashes, it uses this metadata to safely resume exactly where it left off without duplicating data into MinIO.

**Execution:**
We deployed the script using the `spark-submit` command against the Spark Master. To make this work, we included `--packages` which act as plugins, specifically downloading:
* `spark-sql-kafka-0-10` (to talk to Kafka)
* `hadoop-aws` & `aws-java-sdk-bundle` (to execute the `s3a://` protocol to MinIO).

### Final State
Whenever a new comment is posted on the Frontend, it travels entirely asynchronously to the `bronze-raw` directory in the `skyrim-lake` bucket, safely persisted as an analytical Parquet file, fully decoupled from the operational backend.