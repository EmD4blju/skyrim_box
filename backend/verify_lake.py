import pandas as pd
import s3fs

# MinIO connection configuration (matching docker-compose)
storage_options = {
    "key": "minioadmin",
    "secret": "minioadmin123",
    "client_kwargs": {
        "endpoint_url": "http://localhost:9000"
    }
}

# The base path where Spark is writing the parquet files
# Because the stream is partitioned by topic, Pandas will automatically discover all the topics
lake_path = "s3://skyrim-lake/bronze-raw/"

print(f"Attempting to read Parquet data from {lake_path} in MinIO...")

try:
    # Read the dataset directly from MinIO into a Pandas DataFrame
    df = pd.read_parquet(lake_path, storage_options=storage_options)
    
    print("\n" + "="*60)
    print(f"SUCCESS: Found {len(df)} records in the Data Lake")
    print("="*60)
    
    # Display the dataframe with proper formatting
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(df.to_string())
    
except Exception as e:
    print(f"\nFailed to read the Data Lake. Error:")
    print(e)
    print("\nNote: Make sure Spark has written at least one file to the lake. If the topic is completely empty, there will be no Parquet files to read yet.")
