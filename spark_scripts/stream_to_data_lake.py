from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr, from_json

# Initialize SparkSession with required S3/AWS and Kafka packages
spark = SparkSession.builder \
    .appName("SkyrimDataLakeStream") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
    .getOrCreate()

# Ensure Spark logs don't overwhelm the console
spark.sparkContext.setLogLevel("WARN")

print("Starting Spark Streaming from Kafka to MinIO...")

# 1. Read the stream from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:29092") \
    .option("subscribePattern", "skyrim.public.*") \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", "false") \
    .load()

# 2. Extract and transform the Kafka payload
# Kafka values come as binary. We cast them to string.
# Debezium wraps the data in a large JSON. We will save the raw strings as our "Bronze" (Raw) layer.
parsed_df = df.select(
    col("topic"),
    col("timestamp"),
    col("key").cast("string").alias("key_str"),
    col("value").cast("string").alias("value_str")
)

# 3. Write the stream to S3 (MinIO) in JSON format, partitioned by the Kafka topic
query = parsed_df.writeStream \
    .format("parquet") \
    .option("path", "s3a://skyrim-lake/bronze-raw/") \
    .option("checkpointLocation", "s3a://skyrim-lake/checkpoints/bronze-raw/") \
    .partitionBy("topic") \
    .outputMode("append") \
    .start()

query.awaitTermination()
