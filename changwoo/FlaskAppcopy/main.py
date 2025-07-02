from flask import Flask, render_template, jsonify, send_file, request
import json
import folium
from abnormal import detect_abnormal
from obs_data import get_obs_data
from obs_list import ObsCode
import pandas as pd
import matplotlib.dates as mdates
import matplotlib
matplotlib.use('Agg')  # 서버에서 그래프 생성용
import matplotlib.pyplot as plt
import io
import os

# 한글 폰트 설정
matplotlib.rc('font', family='Malgun Gothic')  # 윈도우는 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False     # 마이너스 기호 깨짐 방지

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

@app.route('/uljin')
def uljin_detail():
    obs_code = 'DT_0036'
    city_name = '울진'
    data = get_obs_data({'code': obs_code, 'name': city_name}, url, ServiceKey)
    return render_template('uljin.html',
                           tide_level=data.get('tide_level', 0),
                           wind_speed=data.get('wind_speed', 0),
                           current_speed=data.get('current_speed', 0))

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

import matplotlib.dates as mdates

def plot_graph(city, start_str):
    start_time = pd.to_datetime(start_str)
    end_time = start_time + pd.Timedelta(hours=6)

    month5_path = get_data_path(city, 5)
    month6_path = get_data_path(city, 6)

    dfs = []
    for path in [month5_path, month6_path]:
        if path:
            df = pd.read_csv(path, encoding='cp949')
            for col in ['dt', 'datetime']:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col])
            if 'dt' in df.columns:
                df = df.rename(columns={'dt': 'datetime'})
            dfs.append(df)

    if not dfs:
        plt.figure(figsize=(8, 3))
        plt.text(0.5, 0.5, "데이터 없음", ha='center', va='center', fontsize=20, color='#666666')
        plt.axis('off')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', transparent=True)
        plt.close()
        buf.seek(0)
        return buf

    df_all = pd.concat(dfs)
    df_sel = df_all[(df_all['datetime'] >= start_time) & (df_all['datetime'] <= end_time)]

    plt.figure(figsize=(8, 3), facecolor='#f8fbfe')  # 아주 연한 하늘색 배경
    ax = plt.gca()
    if len(df_sel) > 0:
        # 실제 데이터 파란 실선
        ax.plot(df_sel['datetime'], df_sel['sea_high'], color='#4a90e2', linewidth=2, linestyle='-', label='실제 데이터')
        # 예측 데이터 주황 점선 (6월 데이터)
        june_df = df_sel[df_sel['datetime'] >= pd.Timestamp("2025-06-01 00:00")]
        if not june_df.empty:
            ax.plot(june_df['datetime'], june_df['sea_high'], color='#f5a623', linewidth=2, linestyle='--', label='예측 데이터')
        # 기준선 점선 검정
        ax.axvline(x=pd.Timestamp("2025-06-01 00:00"), color='#333333', linestyle='--', linewidth=1.5, label='기준선')
    else:
        ax.text(0.5, 0.5, "데이터 없음", ha='center', va='center', fontsize=20, color='#666666')
        ax.axis('off')

    ax.set_xlabel("시간", color='#555555')
    ax.set_ylabel("해수면 높이 (cm)", color='#555555')
    ax.set_title(f"{city.title()} 해수면 높이 변화 추이", fontsize=14, color='#333333')

    # 축 스타일 조절
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#cccccc')
    ax.spines['left'].set_color('#cccccc')

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H시"))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    plt.xticks(rotation=45, fontsize=9, color='#555555')
    plt.yticks(color='#555555', fontsize=9)

    ax.grid(True, linestyle=':', linewidth=0.6, color='#cccccc')
    # ax.legend(frameon=False, fontsize=10, loc='upper left')

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True)
    plt.close()
    buf.seek(0)
    return buf


@app.route('/<city>/graph.png')
def city_graph(city):
    start = request.args.get('start', '2025-05-31 21:00:00')
    img = plot_graph(city, start)
    if img:
        return send_file(img, mimetype='image/png')
    else:
        return 'No data', 404

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
