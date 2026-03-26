# Skyrim Box: Big Data Data Engineering Flow

## 1. Project Overview
A platform similar to IMDb or Filmweb, but tailored for **Skyrim items**. The primary goal of this project is not to build a massive production application, but to serve as an educational playground for a modern Big Data pipeline (Debezium, Kafka, Spark, and a Data Lake).

## 2. Core Functionality
- **Authentication:** No explicit login. Users will be identified via a hardcoded identity or an anonymous hash to keep the flow simple.
- **Interactions:** Users can browse a minimal set of Skyrim items and submit comments/reviews on them.
- **Analytics Pipeline:** Every comment cleanly flows from the transactional database into a Data Lake.

## 3. Tech Stack
- **Frontend:** React, TypeScript, TanStack (Query/Router), Tailwind CSS
- **Backend:** Python, FastAPI, SQLModel (Pydantic + SQLAlchemy), Alembic (Migrations)
- **Database:** PostgreSQL (Transactional Store)
- **Big Data Pipeline:**
  - **Debezium:** Change Data Capture (CDC)
  - **Apache Kafka:** Message Broker / Event Streaming
  - **Apache Spark:** Data Processing
  - **Data Lake:** MinIO (S3-compatible local storage) or cloud equivalent

## 4. Data Flow Architecture
1. **User Action:** A user writes a comment on an item via the React Frontend.
2. **API Layer:** FastAPI validates the request and inserts the comment into PostgreSQL using SQLModel.
3. **Change Data Capture:** Debezium monitors the PostgreSQL Write-Ahead Log (WAL), detects the new comment, and pushes an event to an Apache Kafka topic.
4. **Stream Processing:** A Spark Streaming application consumes the events from Kafka.
5. **Data Lake Storage:** Spark writes the processed data into the Data Lake in an analytical format (like Parquet or Delta Lake).

## 5. PostgreSQL Schema Definition (Code-First)
- **User Table:** `id`, `user_hash` / `display_name`, `created_at`
- **Item Table:** `id`, `name`, `description`, `image_url`
- **Comment Table:** `id`, `user_id`, `item_id`, `content`, `created_at`

## 6. Implementation Phases

### Phase 1: Core App Scaffolding
- Initialize the project as a single repository (monorepo) containing frontend, backend, and infrastructure directories.
- Setup PostgreSQL using Docker.
- Define DB tables using **SQLModel** (Code-first approach).
- Configure **Alembic** and apply the initial database migration.
- Seed the DB with a few sample Skyrim items (e.g., Iron Sword, Sweetroll).

### Phase 2: Application Development
- Setup FastAPI endpoints (`GET /items`, `POST /items/{id}/comments`).
- Build basic React UI: Home page list, Item detail page, Comment submission form.
- Implement anonymous/hardcoded user identity attachment for submitted comments.

### Phase 3: Big Data Infrastructure
- Create a `docker-compose.yml` to spin up Kafka, Zookeeper, Debezium, Spark, and MinIO.

### Phase 4: CDC & Streaming 
- Configure PostgreSQL for Logical Replication (required for CDC).
- Deploy the Debezium connector to track changes on the `comments` and `users` tables.
- Verify changes are appearing in Kafka topics.

### Phase 5: The Data Lake
- Write a PySpark script to consume Kafka topics in real-time.
- Transform and write the ingested data into MinIO as Parquet/Delta files.
