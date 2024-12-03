import cbsodata
import pandas as pd
import redis
import json

def store_data(ttl_seconds=600):
    try:
        redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
        
        datasets = {
            2019: "84583NED", 
            2020: "84799NED"  
        }
        
        for year, dataset_id in datasets.items():
            data = pd.DataFrame(cbsodata.get_data(dataset_id, select=['*']))
            data['Gemeentenaam_1'] = data['Gemeentenaam_1'].str.strip()  # text verschonen
            for gemeente, group in data.groupby('Gemeentenaam_1'):
                key = f"kerncijfers:{year}:{gemeente.strip().lower()}"
                print(f"Opslaan sleutel: {key}")
                redis_client.setex(key, ttl_seconds, group.to_json(orient='records'))
        
        print("Alle datasets succesvol opgeslagen in Redis!")
    except Exception as e:
        print(f"Er is een fout opgetreden: {e}")

if __name__ == "__main__":
    store_data()
