import cbsodata
import pandas as pd
import redis
import json

def store_data(ttl_seconds=600):
    try:
        redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

        # Data ophalen
        kerncijfers = "84583NED"
        data_kerncijfers = pd.DataFrame(cbsodata.get_data(kerncijfers, select=['*']))

        # Opschonen van data
        data_kerncijfers = data_kerncijfers.applymap(
            lambda x: x.strip() if isinstance(x, str) else x
        ).fillna('')

        if data_kerncijfers.empty:
            print("Geen data opgehaald uit CBS API.")
            return
        
        # Opslaan in Redis per gemeente
        for gemeente, group in data_kerncijfers.groupby('Gemeentenaam_1'):
            key = f"kerncijfers:{gemeente.strip().lower()}"
            print(f"Opslaan sleutel: {key}")
            redis_client.setex(key, ttl_seconds, group.to_json(orient='records'))

        print("Data succesvol opgesplitst en opgeslagen in Redis!")
    except Exception as e:
        print(f"Er is een fout opgetreden: {e}")

if __name__ == "__main__":
    store_data()