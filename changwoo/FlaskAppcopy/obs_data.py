# obs_data.py

import requests

def safe_float(val):
    try:
        # null, None, '', 'null' 등 문자열/None 모두 0.0 처리
        if val in ('null', None, ''):
            return 0.0
        return float(val)
    except Exception:
        return 0.0

def get_obs_data(obs, url, ServiceKey):
    params = {
        'ServiceKey': ServiceKey,
        'ObsCode': obs['code'],
        'ResultType': 'json'
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            result = response.json().get('result', {})
            data = result.get('data', {})
            meta = result.get('meta', {})
            # data가 dict이 아닐 때 (예: 리스트나 None) 방어
            if not isinstance(data, dict): data = {}
            if not isinstance(meta, dict): meta = {}
            return {
                'tide_level': safe_float(data.get('tide_level', 0)),
                'wind_speed': safe_float(data.get('wind_speed', 0)),
                'current_speed': safe_float(data.get('current_speed', 0)),
                'air_temp': safe_float(data.get('air_temp', 0)),
                'air_press': safe_float(data.get('air_press', 0)),
                'water_temp': safe_float(data.get('water_temp', 0)),
                'obs_lat': safe_float(meta.get('obs_lat', 0)),
                'obs_lon': safe_float(meta.get('obs_lon', 0)),
            }
        else:
            print(f"{obs.get('name','-')} API 통신 오류: {response.status_code}")
            return {}
    except Exception as e:
        print(f"{obs.get('name','-')} 데이터 파싱 오류 :", e)
        return {}
