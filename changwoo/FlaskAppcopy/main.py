from flask import Flask, render_template, jsonify, send_file, request
import json
import folium
from abnormal import detect_abnormal
from obs_data import get_obs_data
from obs_list import ObsCode
import pandas as pd
import matplotlib.dates as mdates
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import os
import chardet

# ========= CSV 자동 인코딩 읽기 =========
def read_csv_autoenc(path):
    with open(path, 'rb') as f:
        enc = chardet.detect(f.read())
    try:
        return pd.read_csv(path, encoding=enc['encoding'])
    except Exception:
        return pd.read_csv(path, encoding='utf-8', errors='replace')

# ========= 데이터 미리 로딩 =========
df4 = read_csv_autoenc('../finalData/Taean_04.csv')
df5 = read_csv_autoenc('../finalData/Taean_05.csv')
df6 = read_csv_autoenc('../pred/this_Taean_06.csv')
df_uljin_5 = read_csv_autoenc('../finalData/Uljin_05.csv')
df_uljin_6 = read_csv_autoenc('../pred/this_Uljin_06.csv')

for df in [df4, df5, df6, df_uljin_5, df_uljin_6]:
    if 'dt' in df.columns:
        df['datetime'] = pd.to_datetime(df['dt'])
    elif 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'])

matplotlib.rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False

app = Flask(__name__)

url = 'http://www.khoa.go.kr/api/oceangrid/tideObsRecent/search.do'
ServiceKey = 'c2jVwblwmcHB5tOEWxEjbg=='

with open('./observatory/jo.json', encoding='utf-8') as f:
    ObsCode_json = json.load(f)
with open('./observatory/bui.json', encoding='utf-8') as f:
    BuiCode_json = json.load(f)

# ========= 대시보드 =========
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

# ========= 상세페이지 =========
@app.route('/incheon')
def incheon_detail():
    obs_code = 'DT_0011'
    city_name = '인천'
    data = get_obs_data({'code': obs_code, 'name': city_name}, url, ServiceKey)
    return render_template('incheon.html',
                           tide_level=data.get('tide_level', 0),
                           wind_speed=data.get('wind_speed', 0),
                           current_speed=data.get('current_speed', 0))

@app.route('/taean')
def taean_detail():
    obs_code = 'DT_0025'
    city_name = '태안'
    data = get_obs_data({'code': obs_code, 'name': city_name}, url, ServiceKey)
    return render_template('taean.html',
                           tide_level=data.get('tide_level', 0),
                           wind_speed=data.get('wind_speed', 0),
                           current_speed=data.get('current_speed', 0))

@app.route('/uljin')
def uljin_detail():
    obs_code = 'DT_0036'
    city_name = '울진'
    data = get_obs_data({'code': obs_code, 'name': city_name}, url, ServiceKey)
    print(df_uljin_5.columns)
    print(df_uljin_6.columns)
    print(df_uljin_5['sea_dir_i'].tail(20))
    print(df_uljin_6['sea_dir_i'].head(20))

    return render_template('uljin.html',
                           tide_level=data.get('tide_level', 0),
                           wind_speed=data.get('wind_speed', 0),
                           current_speed=data.get('current_speed', 0))

@app.route('/tongyeong')
def tongyeong_detail():
    obs_code = 'DT_0040'
    city_name = '통영'
    data = get_obs_data({'code': obs_code, 'name': city_name}, url, ServiceKey)
    return render_template('tongyeong.html',
                           tide_level=data.get('tide_level', 0),
                           wind_speed=data.get('wind_speed', 0),
                           current_speed=data.get('current_speed', 0))

@app.route('/yeosu')
def yeosu_detail():
    obs_code = 'DT_0041'
    city_name = '여수'
    data = get_obs_data({'code': obs_code, 'name': city_name}, url, ServiceKey)
    return render_template('yeosu.html',
                           tide_level=data.get('tide_level', 0),
                           wind_speed=data.get('wind_speed', 0),
                           current_speed=data.get('current_speed', 0))

# ========= 그래프 엔드포인트 (태안) =========
@app.route('/taean/graph.png')
def taean_graph():
    col = request.args.get('col', 'sea_high')
    start_str = request.args.get('start', '2025-05-31 21:00:00')
    df_real = pd.concat([df4, df5])
    df_pred = df6
    return send_file(plot_graph(df_real, df_pred, col, start_str), mimetype='image/png')

# ========= 그래프 엔드포인트 (울진) =========
@app.route('/uljin/graph.png')
def uljin_graph():
    col = request.args.get('col', 'sea_high')
    start_str = request.args.get('start', '2025-05-31 21:00:00')
    return send_file(plot_graph(df_uljin_5, df_uljin_6, col, start_str), mimetype='image/png')

# ========= 그래프 공통 함수 =========
def plot_graph(df_real, df_pred, col, start_str):
    start_time = pd.to_datetime(start_str)
    end_time = start_time + pd.Timedelta(hours=6)
    df_real_sel = df_real[(df_real['datetime'] >= start_time) & (df_real['datetime'] < end_time)]
    df_pred_sel = df_pred[(df_pred['datetime'] >= start_time) & (df_pred['datetime'] < end_time)]
    plt.figure(figsize=(18, 8), facecolor='#eaf3fb')
    ax = plt.gca()
    if not df_real_sel.empty and col in df_real_sel:
        ax.plot(df_real_sel['datetime'], df_real_sel[col], color='#2577e3', linewidth=4, marker='o', markersize=9, alpha=0.97)
    if not df_pred_sel.empty and col in df_pred_sel:
        ax.plot(df_pred_sel['datetime'], df_pred_sel[col], color='#ff8a57', linewidth=4, marker='o', markersize=9, linestyle='--', alpha=0.88)
    june_start = pd.Timestamp('2025-06-01 00:00:00')
    if not df_real_sel.empty and not df_pred_sel.empty:
        if (df_real_sel['datetime'] < june_start).any() and (df_pred_sel['datetime'] >= june_start).any():
            ax.axvline(x=june_start, color='#888', linestyle='--', linewidth=2.6, alpha=0.72)
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_title('')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#bfd7ee')
    ax.spines['bottom'].set_color('#bfd7ee')
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d\n%H시"))
    plt.xticks(rotation=28, fontsize=20, color='#222')
    plt.yticks(fontsize=20, color='#222')
    ax.grid(True, linestyle=':', linewidth=1.2, color='#c9e0f7', alpha=0.94)
    plt.tight_layout(pad=0.5)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True, dpi=140)
    plt.close()
    buf.seek(0)
    return buf

# ========= 지도(관측소) =========
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

# ========= API =========
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

@app.route('/tidedata')
def tidedata():
    target_names = ['인천', '통영', '태안', '여수', '울진']
    selected_obs = [obs for obs in ObsCode if obs['name'] in target_names]
    tide_data = []
    for obs in selected_obs:
        result = get_obs_data(obs, url, ServiceKey)
        tide_level = result.get('tide_level', 0) if result else 0
        tide_data.append({'name': obs['name'], 'tide_level': tide_level})
    return jsonify(tide_data)

# ========= 데이터 경로 유틸 =========
def get_data_path(city, month):
    city_map = {
        'incheon': 'InCheon',
        'taean': 'Taean',
        'tongyeong': 'TongYeong',
        'yeosu': 'Yeosu',
        'uljin': 'Uljin'
    }
    city_name = city_map.get(city.lower())
    if not city_name:
        return None
    if month == 6:
        path = f'../pred/this_{city_name}_06.csv'
    else:
        path = f'../finalData/{city_name}_05.csv'
    return path if os.path.exists(path) else None

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
