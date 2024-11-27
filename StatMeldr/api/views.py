from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import pandas as pd
import redis
import json

def get_filtered_data(request):
    try:
        redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

        selected_gemeente = request.GET.get('gemeente', 'Heerlen').strip().lower()
        key = f"kerncijfers:{selected_gemeente}"

        print(f"Op te halen sleutel: {key}")

        cached_data = redis_client.get(key)
        if not cached_data:
            return render(request, 'api/cbs_data.html', {'data': []})


        json_data = json.loads(cached_data) #json gebruiken ipv pandas, pandas geeft future error warnings dat pd.read_json depricated wordt
        print(f"Geparsed JSON data: {json_data[:3]}")  

        filtered_data = [
            {key: item[key] for key in ['WijkenEnBuurten', 'Gemeentenaam_1']}
            for item in json_data
        ]

        return render(request, 'api/cbs_data.html', {'data': filtered_data})
    except Exception as e:
        print(f"Er is een fout opgetreden: {e}")
        return JsonResponse({'error': f'Er is een fout opgetreden: {e}'}, status=500)



def get_filtered_data_csv(request):
    """
    Haalt gefilterde data op uit Redis en retourneert deze als een CSV-bestand.
    """
    try:
        # Redis-client configureren
        redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

        # Ophalen van data uit Redis
        cached_data = redis_client.get('kerncijfers2019')
        if not cached_data:
            return JsonResponse({'error': 'Data niet gevonden in Redis'}, status=404)

        # Laden van data in een Pandas DataFrame
        data_kerncijfers = pd.read_json(cached_data, orient='records')

        # Filteren op Gemeentenaam_1 == "Heerlen" en alleen specifieke kolommen behouden
        filtered_data = data_kerncijfers[
            data_kerncijfers['Gemeentenaam_1'] == 'Heerlen'
        ][['WijkenEnBuurten', 'Gemeentenaam_1']]

        # HTTP-respons voor CSV-bestand
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="filtered_data.csv"'

        # Schrijf de gefilterde data naar het CSV-bestand
        filtered_data.to_csv(response, index=False)
        return response
    except Exception as e:
        return JsonResponse({'error': f'Er is een fout opgetreden: {e}'}, status=500)
