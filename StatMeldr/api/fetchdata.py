import pandas as pd
import redis

def fetch_data():
    try:
        redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
        data_as_json = redis_client.get('kerncijfers2019')
        if data_as_json:
            
            data_as_json_str = data_as_json.decode('utf-8') #bytes omzetten naar strings

            data_kerncijfers = pd.read_json(data_as_json_str, orient='records')
            print(data_kerncijfers.head())
        else:
            print("Geen data gevonden in Redis onder de sleutel 'cbs_kerncijfers'.")
    except Exception as e:
        print(f"Er is een fout opgetreden: {e}")

if __name__ == "__main__":
    fetch_data()
