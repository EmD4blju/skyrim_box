import requests
import json
import time

DEBEZIUM_URL = "http://localhost:8083/connectors"

CONNECTOR_CONFIG = {
    "name": "skyrim-postgres-connector",
    "config": {
        "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
        "plugin.name": "pgoutput",
        "database.hostname": "postgres", # Connects via Docker internal network
        "database.port": "5432",
        "database.user": "skyrim_user",
        "database.password": "skyrim_password",
        "database.dbname": "skyrim_db",
        "topic.prefix": "skyrim", # Maps topics to skyrim.public.item, ...
        # Include the tables we care about (users, items, and comments)
        "table.include.list": "public.user,public.item,public.comment",
        # Ensure we don't drop timezone info completely
        "time.precision.mode": "connect"
    }
}

def register_connector():
    print("Checking if Debezium is ready...")
    for _ in range(10):
        try:
            res = requests.get(DEBEZIUM_URL)
            if res.status_code == 200:
                print("Debezium is reachable. Registering connector...")
                break
        except requests.exceptions.ConnectionError:
            pass
        
        print("Waiting for Debezium on localhost:8083...")
        time.sleep(2)
    else:
        print("Failed to reach Debezium.")
        return

    # Delete existing connector if it exists to allow re-running this script
    requests.delete(f"{DEBEZIUM_URL}/skyrim-postgres-connector")
    
    # Create the new connector
    headers = {"Content-Type": "application/json"}
    response = requests.post(DEBEZIUM_URL, data=json.dumps(CONNECTOR_CONFIG), headers=headers)
    
    if response.status_code in [200, 201]:
        print("✅ Connector registered successfully!")
        print(json.dumps(response.json(), indent=2))
    elif response.status_code == 409:
        print("⚠️ Connector already exists!")
    else:
        print(f"❌ Failed to register connector. Status code: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    register_connector()
