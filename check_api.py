def obtener_datos(fecha):
    url = "https://www.datos.gov.co/resource/s54a-sgyg.json"
    params = {
        '$where': f"fechaobservacion >= '{fecha}T00:00:00' AND fechaobservacion < '{fecha}T23:59:59'",
        '$limit': 5000
    }
    response = requests.get(url, params=params)

    print(f"Fetching data for {fecha} - Status: {response.status_code}")
    if response.status_code != 200:
        print("Error fetching data:", response.text)  # Print error details
        return []
    
    data = response.json()
    print(f"Records received: {len(data)}")  # Debugging output
    return data
