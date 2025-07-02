import requests

def get_obs_data(obs, url, ServiceKey):
    """
    관측소 실시간 데이터 파싱 함수

    :param obs: {'name': '인천', 'code': 'DT_0011', ...}
    :param url: API 엔드포인트 URL
    :param ServiceKey: KHOA API 서비스 키
    :return: 데이터 dict (실패시 값은 '-' 또는 0)
    """
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
            res_json = response.json()
            data = res_json['result']['data']
            meta = res_json['result']['meta']
            # null, None, '' 등 모두 안전하게 float 변환
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
