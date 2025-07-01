import requests

def get_obs_data(obs, url, ServiceKey):
  params = {
    'ServiceKey' : ServiceKey,
    'ObsCode' : obs['code'],
    'ResultType' : 'json'
  }
  response = requests.get(url, params=params)
  
  if response.status_code == 200:
    try:
      data = response.json()['result']['data']
      return {
        'tide_level' : float(data.get('tide_level', 0) or 0),
        'wind_speed' : float(data.get('wind_speed', 0) or 0),
        'current_speed' : float(data.get('current_speed', 0) or 0),
        'air_temp' : float(data.get('air_temp', 0) or 0),
        'air_press' : float(data.get('air_press', 0) or 0),
        'water_temp' : float(data.get('water_temp', 0) or 0),
      }
    except Exception as e:
      print(obs['name'], '데이터 파싱 오류 :', e)
      return {}
  else:
    print(obs['name'], 'API 통신 오류 :', response.status_code)
    return {}