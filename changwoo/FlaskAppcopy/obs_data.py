import requests

def get_obs_data(obs, url, ServiceKey):
    params = {
        'ServiceKey': ServiceKey,
        'ObsCode': obs['code'],
        'ResultType': 'json'
    }
    try:
        response = requests.get(url, params=params, timeout=4)
    except Exception as ex:
        print(f"[{obs.get('name', '')}] API 요청 에러:", ex)
        return {}

    if response.status_code == 200:
        try:
            # 실제로 JSON인지 검사
            try:
                res_json = response.json()
            except Exception as e:
                print(f"[{obs.get('name', '')}] JSON 디코딩 오류: {e}, 응답: {response.text}")
                return {}
            
            # 에러 응답 구조 방어
            if 'result' in res_json and 'error' in res_json['result']:
                print(f"[{obs.get('name', '')}] API 에러: {res_json['result']['error']}")
                return {}

            # 정상 데이터 구조 방어
            data = res_json.get('result', {}).get('data')
            meta = res_json.get('result', {}).get('meta')
            if data is None or meta is None:
                print(f"[{obs.get('name', '')}] 데이터 파싱 오류 : 'data' or 'meta' 없음")
                return {}

            def safe_float(x):
                try:
                    return float(x) if x not in (None, '', 'null') else 0
                except:
                    return 0

            return {
                'tide_level'   : safe_float(data.get('tide_level', 0)),
                'wind_speed'   : safe_float(data.get('wind_speed', 0)),
                'current_speed': safe_float(data.get('current_speed', 0)),
                'air_temp'     : safe_float(data.get('air_temp', 0)),
                'air_press'    : safe_float(data.get('air_press', 0)),
                'water_temp'   : safe_float(data.get('water_temp', 0)),
                'obs_lat'      : safe_float(meta.get('obs_lat', 0)),
                'obs_lon'      : safe_float(meta.get('obs_lon', 0)),
            }
        except Exception as e:
            print(f"[{obs.get('name', '')}] 데이터 파싱 오류:", e)
            return {}
    else:
        print(f"[{obs.get('name', '')}] API 통신 오류:", response.status_code)
        return {}
