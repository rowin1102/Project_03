from flask import Flask, render_template, jsonify
import json, folium, requests
from abnormal import detect_abnormal
from obs_data import get_obs_data
from obs_list import ObsCode
import os
import datetime

print(os.listdir(os.path.join(os.path.dirname(__file__), "templates")))
print("MAIN.PY PATH >>>", __file__)

app = Flask(__name__)

# 🔑 ServiceKey 한 번만 선언 (여기에 본인 API키 입력!)
ServiceKey = 'uHRQY9ctKuLtELm0nTRpg=='

url = 'http://www.khoa.go.kr/api/oceangrid/tideObsRecent/search.do'

with open('./observatory/jo.json', encoding='utf-8') as f:
    ObsCode_json = json.load(f)
with open('./observatory/bui.json', encoding='utf-8') as f:
    BuiCode_json = json.load(f)

# 👇 만조/간조 실시간 정보 함수 (항구코드 넘기면 각 항구 가능)
def get_high_low_tide(port_code):
    today = datetime.datetime.now().strftime('%Y%m%d')
    url_tide = (
        'http://www.khoa.go.kr/api/oceangrid/tideObsTide/search.do'
        f'?ServiceKey={ServiceKey}&ObsCode={port_code}&Date={today}&ResultType=json'
    )
    try:
        res = requests.get(url_tide)
        if res.status_code != 200:
            return ('-', '-')
        data = res.json()
        # 'null' 값 거르기!
        tide_list = [item for item in data.get('result', {}).get('data', [])
                     if item.get('maxwl') not in ('null', None) and item.get('minwl') not in ('null', None)]
        if not tide_list:
            return ('-', '-')
        high = max(tide_list, key=lambda t: float(t['maxwl']))
        low = min(tide_list, key=lambda t: float(t['minwl']))
        high_time = high['httime']
        high_wl = high['maxwl']
        low_time = low['lttime']
        low_wl = low['minwl']
        high_tide = f"{high_time} ({high_wl}cm)"
        low_tide = f"{low_time} ({low_wl}cm)"
        return (high_tide, low_tide)
    except Exception as e:
        print("만조/간조 API 오류:", e)
        return ('-', '-')


# 각 항구별 KHOA 관측소 코드 맵
PORT_CODES = {
    "incheon":  'DT_0011',
    "taean":    'DT_0025',
    "tongyeong":'DT_0040',
    "yeosu":    'DT_0041',
    "uljin":    'DT_0036',
}

@app.route('/')
def dashboard():
    warning_msg = []
    danger_msg = []
    for obs in ObsCode:
        data = get_obs_data(obs, url, ServiceKey)
        warning = detect_abnormal(data)
        for w in warning:
            warning_msg.append(f"{obs['name']} {w}") 
        if any('위험' in w for w in warning):
            danger_msg.append(f"{obs['name']} 출항 금지")
    return render_template('mainPage.html', warning=warning_msg, danger_area=danger_msg)

@app.route('/api/warning')
def api_warning():
    warning_msg = []
    for obs in ObsCode:
        data = get_obs_data(obs, url, ServiceKey)
        warning = detect_abnormal(data)
        for w in warning:
            warning_msg.append(f"{obs['name']} {w}") 
    return jsonify({'warning': warning_msg})

@app.route('/api/danger_area')
def api_danger_area():
    danger_msg = []
    for obs in ObsCode:
        data = get_obs_data(obs, url, ServiceKey)
        warning = detect_abnormal(data)
        if any('위험' in w for w in warning):
            danger_msg.append(f"{obs['name']} 출항 금지")
    return jsonify({'danger_area': danger_msg})

# 👇 각 항구별 상세 (만조/간조 정보 같이 넘김)
@app.route('/incheon')
def incheon_detail():
    high_tide, low_tide = get_high_low_tide(PORT_CODES['incheon'])
    return render_template('incheon.html', high_tide=high_tide, low_tide=low_tide)

@app.route('/taean')
def taean_detail():
    high_tide, low_tide = get_high_low_tide(PORT_CODES['taean'])
    return render_template('taean.html', high_tide=high_tide, low_tide=low_tide)

@app.route('/tongyeong')
def tongyeong_detail():
    high_tide, low_tide = get_high_low_tide(PORT_CODES['tongyeong'])
    return render_template('tongyeong.html', high_tide=high_tide, low_tide=low_tide)

@app.route('/yeosu')
def yeosu_detail():
    high_tide, low_tide = get_high_low_tide(PORT_CODES['yeosu'])
    return render_template('yeosu.html', high_tide=high_tide, low_tide=low_tide)

@app.route('/uljin')
def uljin_detail():
    high_tide, low_tide = get_high_low_tide(PORT_CODES['uljin'])
    return render_template('uljin.html', high_tide=high_tide, low_tide=low_tide)

@app.route('/obs_map')
def obs_map():
    m = folium.Map(location=[36.5, 127.8], zoom_start=6, width="100%", height="420px")

    url_jo = 'http://www.khoa.go.kr/api/oceangrid/tideObsRecent/search.do'
    for name, code in ObsCode_json.items():
        obs = {'code': code, 'name': name}
        data = get_obs_data(obs, url_jo, ServiceKey)
        lat = 35.1
        lon = 129.1
        try:
            lat = float(data.get('obs_lat', lat))
            lon = float(data.get('obs_lon', lon))
            popup = f"""<b>조위관측소</b><br>
                {name}<br>
                수온: {data.get('water_temp', '')} ℃<br>
                기온: {data.get('air_temp', '')} ℃<br>
                기압: {data.get('air_press', '')} hPa<br>
                풍속: {data.get('wind_speed', '')} m/s<br>
                조위: {data.get('tide_level', '')} cm<br>
                유속: {data.get('current_speed', '')} m/s
                """
            folium.Marker([lat, lon], tooltip=popup,
                icon=folium.Icon(icon='home', prefix='fa', color='orange')).add_to(m)
        except Exception as e:
            print(f'조위관측소 {name} 위치 정보 없음: {e}')

    url_bui = 'http://www.khoa.go.kr/api/oceangrid/buObsRecent/search.do'
    for name, code in BuiCode_json.items():
        obs = {'code': code, 'name': name}
        data = get_obs_data(obs, url_bui, ServiceKey)
        lat = 34.5
        lon = 126.5
        try:
            lat = float(data.get('obs_lat', lat))
            lon = float(data.get('obs_lon', lon))
            popup = f"""<b>해양관측부이</b><br>
                    {name}<br>
                    수온: {data.get('water_temp', '')} ℃<br>
                    기온: {data.get('air_temp', '')} ℃<br>
                    기압: {data.get('air_press', '')} hPa<br>
                    풍속: {data.get('wind_speed', '')} m/s<br>
                    유속: {data.get('current_speed', '')} cm/s
                    """
            folium.Marker(
                location=[lat, lon], tooltip=popup,
                icon=folium.Icon(icon='star', prefix='fa', color='blue')
            ).add_to(m)
        except Exception as e:
            print(f'부이 {name} 위치 정보 없음: {e}')
    html = m._repr_html_()
    return html

@app.route('/piechart')
def piechart():
    return render_template('chart05.html')

@app.route('/winddata')
def winddata():
    target_names = ['인천', '통영', '태안', '여수', '울진']
    selected_obs = [obs for obs in ObsCode if obs['name'] in target_names]

    wind_data = []
    for obs in selected_obs:
        result = get_obs_data(obs, url, ServiceKey)
        wind_speed = result.get('wind_speed', 0) if result else 0
        wind_data.append({'name': obs['name'], 'wind_speed': wind_speed})

    return jsonify(wind_data)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
