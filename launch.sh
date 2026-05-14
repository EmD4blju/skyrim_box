#!/bin/bash

echo "========================================"
echo " Starting Skyrim Box Data System"
echo "========================================"

echo "[1/6] Starting background infrastructure (Docker)..."
docker compose up -d

echo "Waiting for services (PostgreSQL, Kafka, Debezium) to initialize (15 seconds)..."
sleep 15

echo "[3/6] Setting up Debezium Connectors..."
# Note: Ensure you have "requests" installed in your environment if this script uses it
python setup_debezium.py

echo "[4/6] Submitting PySpark Job to Spark Master..."
# Using -d to run the docker exec in detached mode so it doesn't block the terminal
docker exec -d skyrim_spark_master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --conf spark.jars.ivy=/tmp/.ivy \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262 \
  /opt/spark/work-dir/stream_to_data_lake.py

echo "[5/6] Starting Backend API..."
cd backend
uv run main.py &
BACKEND_PID=$!
cd ..

echo "[6/6] Starting Frontend..."
cd frontend
npm install
npm run dev &
FRONTEND_PID=$!
cd ..

echo "========================================"
echo " All services started!"
echo " - Frontend: http://localhost:5173"
echo " - Backend API: http://localhost:8000"
echo " - Kafka UI: http://localhost:8090"
echo " - MinIO Console: http://localhost:9001"
echo " - Spark Master UI: http://localhost:8080"
echo "========================================"
echo "Press Ctrl+C to stop both Backend and Frontend servers."

# Trap SIGINT (Ctrl+C) and kill the background processes
trap "echo 'Stopping local servers...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT

# Wait for background processes to keep script running
wait $FRONTEND_PID $BACKEND_PID
