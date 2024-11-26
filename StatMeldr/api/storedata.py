import cbsodata
import pandas as pd
import redis
import json

def store_data(ttl_seconds = 600):
    try:
        redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
        kerncijfers = "84583NED"
        data_kerncijfers = pd.DataFrame(
            cbsodata.get_data(kerncijfers, select=['*'])
        )
        data_kerncijfers = data_kerncijfers.applymap(
            lambda x: x.strip() if isinstance(x, str) else x
        ).fillna('')
        data_as_json = data_kerncijfers.to_json(orient='records')
        redis_client.setex('kerncijfers2019', ttl_seconds, data_as_json)
        print("Data succesvol opgeslagen in Redis!")
    except Exception as e:
        print(f"Er is een fout opgetreden: {e}")

if __name__ == "__main__":
    store_data()
