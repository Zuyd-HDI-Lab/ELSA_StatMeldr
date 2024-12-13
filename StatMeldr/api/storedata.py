import requests
import xml.etree.ElementTree as ET
import cbsodata
import pandas as pd
import redis
import json

def store_cbs_data(ttl_seconds=1200):
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


def store_rivm_data(ttl_seconds=1200):
    redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

    url = "https://dataderden.cbs.nl/ODataFeed/odata/50120NED/TypedDataSet"
    perioden = ['2020JJ00', '2022JJ00']
    leeftijden = ['20300', '53115', '80200']
    marges = "MW00000"
    batch_size = 1000  

    for period in perioden:
        for age in leeftijden:
            skip = 0
            all_rows = []
            while True: 
                params = { #Je moet een skip en top instellen, want net als bij cbs is er een limiet op de api call. Zo kan je alsnog alles ophalen.
                    "$filter": f"(Perioden eq '{period}') and (Marges eq '{marges}') and (Leeftijd eq '{age}')",
                    "$top": batch_size,
                    "$skip": skip
                }
                print(f"Ophalen data voor Periode: {period}, Leeftijd: {age}, Skip: {skip}")

                try:
                    response = requests.get(url, params=params)
                    if response.status_code != 200:
                        print(f"Fout bij ophalen data: {response.status_code}")
                        break

                    xml_content = response.text
                    root = ET.fromstring(xml_content)

                    rows = []
                    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                        content = entry.find('{http://www.w3.org/2005/Atom}content')
                        if content is not None:
                            properties = content.find('{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}properties')
                            if properties is not None:
                                row = {}
                                for prop in properties:
                                    tag_name = prop.tag.split('}')[-1]
                                    value = prop.text.strip() if prop.text else None
                                    row[tag_name] = value
                                rows.append(row)

                    if not rows:
                        print("Geen records meer gevonden.")
                        break

                    all_rows.extend(rows)
                    skip += batch_size  

                except Exception as e:
                    print(f"Er is een fout opgetreden tijdens het ophalen of verwerken: {e}")
                    break

            if all_rows:
                df = pd.DataFrame(all_rows)

                if "Gemeentenaam_1" not in df.columns:
                    print("Kolom 'Gemeentenaam_1' ontbreekt in de dataset.")
                    continue

                for gemeente, group in df.groupby("Gemeentenaam_1"):
                    if not gemeente:  
                        print("Gemeente-naam ontbreekt in deze dataset. Data wordt overgeslagen.")
                        continue

                    key = f"rivm:{period}:{age}:{gemeente.strip().lower()}"
                    try:
                        redis_client.setex(key, ttl_seconds, group.to_json(orient="records"))
                        print(f"Gemeente '{gemeente}' succesvol opgeslagen onder sleutel: {key}")
                    except Exception as e:
                        print(f"Fout bij opslaan van gemeente '{gemeente}': {e}")



if __name__ == "__main__":
     store_cbs_data()
     store_rivm_data()
