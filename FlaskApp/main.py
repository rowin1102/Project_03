from flask import Flask, render_template, jsonify
import json, json, folium
from abnormal import detect_abnormal
from obs_data import get_obs_data
from obs_list import ObsCode

app = Flask(__name__)

url = 'http://www.khoa.go.kr/api/oceangrid/tideObsRecent/search.do'
ServiceKey = 'uHRQY9ctKuLtELm0nTRpg=='

with open('./observatory/jo.json', encoding='utf-8') as f:
    ObsCode_json = json.load(f)
with open('./observatory/bui.json', encoding='utf-8') as f:
    BuiCode_json = json.load(f)

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
def index():
    return render_template('mainPage.html')

@app.route('/api/warning')
def api_warning():
  warning_msg = []
  for obs in ObsCode:
    data = get_obs_data(obs, url, ServiceKey)
    warning = detect_abnormal(data)
    for w in warning:
      warning_msg.append(f"{obs['name']} {w}") 
  return jsonify({'warning' : warning_msg})

@app.route('/api/danger_area')
def api_danger_area():
  danger_msg = []
  for obs in ObsCode:
    data = get_obs_data(obs, url ,ServiceKey)
    warning = detect_abnormal(data)
    if any('위험' in w for w in warning):
      danger_msg.append(f"{obs['name']} 출항 금지")
  return jsonify({'danger_area' : danger_msg})

@app.route('/incheon')
def incheon_detail():
    return render_template('incheon.html')

@app.route('/taean')
def taean_detail():
    return render_template('taean.html')

@app.route('/tongyeong')
def tongyeong_detail():
    return render_template('tongyeong.html')

@app.route('/yeosu')
def yeosu_detail():
    return render_template('yeosu.html')

@app.route('/uljin')
def uljin_detail():
    return render_template('uljin.html')

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

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8080, debug=True)