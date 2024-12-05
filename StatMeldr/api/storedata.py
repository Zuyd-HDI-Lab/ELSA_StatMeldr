import cbsodata
import pandas as pd
import redis
import json

def store_data(ttl_seconds=600):
    try:
        redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
        
        datasets = {
            "kerncijfers": {
                "2019": "84583NED",
                "2020": "84799NED",
            },
            "uitkeringen": {
                "2019": "84692NED",
                "2020": "84897NED",
            },
        }
        
        for dataset_name, years in datasets.items():
            for year, dataset_id in years.items():
                print(f"Ophalen dataset: {dataset_name}, jaar: {year}, id: {dataset_id}")
                data = pd.DataFrame(cbsodata.get_data(dataset_id, select=["*"]))

                # Schoonmaken van de data
                for column in data.select_dtypes(include=['object']):
                    data[column] = data[column].map(lambda x: x.strip() if isinstance(x, str) else x)

                # Data splitsen per gemeente groep, en dan opslaan.
                for gemeente, group in data.groupby("Gemeentenaam_1"):
                        gemeente = gemeente.strip()  
                        if not gemeente: 
                            continue
                        key = f"{dataset_name}:{year}:{gemeente.strip().lower()}"
                        print(f"Opslaan sleutel: {key}")
                        redis_client.setex(key, ttl_seconds, group.to_json(orient="records"))
   
        print("Alle datasets succesvol opgeslagen in Redis!")
    except Exception as e:
        print(f"Er is een fout opgetreden: {e}")

if __name__ == "__main__":
    store_data()
