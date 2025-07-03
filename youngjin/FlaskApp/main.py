from flask import Flask, render_template, jsonify
import json, json, folium
import pandas as pd
from abnormal import detect_abnormal
from obs_data import get_obs_data
from obs_list import ObsCode

app = Flask(__name__)

url = 'http://www.khoa.go.kr/api/oceangrid/tideObsRecent/search.do'
ServiceKey = 'c2jVwblwmcHB5tOEWxEjbg=='

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
    obs_code = 'DT_0011'
    data = get_obs_data({'code': obs_code, 'name': '인천'}, url, ServiceKey)
    tide_level = data.get('tide_level', 0)
    wind_speed = data.get('wind_speed', 0)
    current_speed = data.get('current_speed', 0)
    return render_template(
        'incheon.html',
        tide_level=tide_level,
        wind_speed=wind_speed,
        current_speed=current_speed
    )

@app.route('/taean')
def taean_detail():
    obs_code = 'DT_0025'
    data = get_obs_data({'code': obs_code, 'name': '태안'}, url, ServiceKey)
    tide_level = data.get('tide_level', 0)
    wind_speed = data.get('wind_speed', 0)
    current_speed = data.get('current_speed', 0)
    return render_template(
        'taean.html',
        tide_level=tide_level,
        wind_speed=wind_speed,
        current_speed=current_speed
    )

@app.route('/tongyeong')
def tongyeong_detail():
    obs_code = 'DT_0040'
    data = get_obs_data({'code': obs_code, 'name': '통영'}, url, ServiceKey)
    tide_level = data.get('tide_level', 0)
    wind_speed = data.get('wind_speed', 0)
    current_speed = data.get('current_speed', 0)
    return render_template(
        'tongyeong.html',
        tide_level=tide_level,
        wind_speed=wind_speed,
        current_speed=current_speed
    )

@app.route('/yeosu')
def yeosu_detail():
    obs_code = 'DT_0041'
    data = get_obs_data({'code': obs_code, 'name': '여수'}, url, ServiceKey)
    tide_level = data.get('tide_level', 0)
    wind_speed = data.get('wind_speed', 0)
    current_speed = data.get('current_speed', 0)
    return render_template(
        'yeosu.html',
        tide_level=tide_level,
        wind_speed=wind_speed,
        current_speed=current_speed
    )

@app.route('/uljin')
def uljin_detail():
    obs_code = 'DT_0036'
    data = get_obs_data({'code': obs_code, 'name': '울진'}, url, ServiceKey)
    tide_level = data.get('tide_level', 0)
    wind_speed = data.get('wind_speed', 0)
    current_speed = data.get('current_speed', 0)
    return render_template(
        'uljin.html',
        tide_level=tide_level,
        wind_speed=wind_speed,
        current_speed=current_speed
    )

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

@app.route('/winddata')
def winddata():
    target_names = ['인천', '통영', '태안', '여수', '울진']
    selected_obs = [obs for obs in ObsCode if obs['name'] in target_names]

    wind_data = []
    for obs in selected_obs:
        result = get_obs_data(obs, url, ServiceKey)  # 여기서 항상 최신 데이터를 호출
        wind_speed = result.get('wind_speed', 0) if result else 0
        wind_data.append({'name': obs['name'], 'wind_speed': wind_speed})

    return jsonify(wind_data)

@app.route('/tidedata')
def tidedata():
    target_names = ['인천', '통영', '태안', '여수', '울진']
    selected_obs = [obs for obs in ObsCode if obs['name'] in target_names]

    tide_data = []
    for obs in selected_obs:
        result = get_obs_data(obs, url, ServiceKey)  # 최신 데이터 호출
        tide_level = result.get('tide_level', 0) if result else 0
        tide_data.append({'name': obs['name'], 'tide_level': tide_level})

    return jsonify(tide_data)

@app.route('/api/incheon_chart_data')
def incheon_chart_data():
    obs_df = pd.read_csv('../finalData/InCheon_05.csv')
    pred_df = pd.read_csv('../pred/this_InCheon_06.csv')

    def parse(df):
        df['datetime'] = pd.to_datetime(df['datetime']).dt.strftime('%Y-%m-%dT%H:%M:%S')
        return df[['datetime', 'sea_high', 'wind_speed', 'pressure', 'sea_speed']]\
            .rename(columns={'wind_speed': 'wind_speed'})\
            .dropna()

    obs = parse(obs_df)
    pred = parse(pred_df)

    return jsonify({
        'observed': obs.to_dict(orient='records'),
        'predicted': pred.to_dict(orient='records')
    })

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8080, debug=True)