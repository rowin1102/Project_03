from flask import Flask, render_template, jsonify, send_file, request
import json
import folium
import io
import chardet
import pandas as pd
from abnormal import detect_abnormal
from obs_data import get_obs_data
from obs_list import ObsCode
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

app = Flask(__name__)

# ========= CSV 자동 인코딩 읽기 =========
def read_csv_autoenc(path):
    with open(path, 'rb') as f:
        enc = chardet.detect(f.read())
    try:
        return pd.read_csv(path, encoding=enc['encoding'])
    except:
        return pd.read_csv(path, encoding='utf-8', errors='replace')

# ========= 데이터 미리 로딩 (태안만) =========
df4 = read_csv_autoenc('./static/finalData/Taean_04.csv')
df5 = read_csv_autoenc('./static/finalData/Taean_05.csv')
df6 = read_csv_autoenc('../pred/this_Taean_06.csv')

for df in (df4, df5, df6):
    if 'dt' in df.columns:
        df['datetime'] = pd.to_datetime(df['dt'])
    else:
        df['datetime'] = pd.to_datetime(df['datetime'])

# 한글 폰트 설정
matplotlib.rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False

def show_value(v):
    if v in (None, '', 'null', 0):
        return '-'
    return str(v)

# ========= 공통 설정 =========
url = 'http://www.khoa.go.kr/api/oceangrid/tideObsRecent/search.do'
ServiceKey = 'uHRQY9ctKuLtELm0nTRpg=='
with open('./observatory/jo.json', encoding='utf-8') as f:
    ObsCode_json = json.load(f)
with open('./observatory/bui.json', encoding='utf-8') as f:
    BuiCode_json = json.load(f)

# ========= 대시보드 =========
@app.route('/')
def dashboard():
    warning_msg, danger_area = [], []
    for obs in ObsCode:
        data = get_obs_data(obs, url, ServiceKey)
        for w in detect_abnormal(data):
            warning_msg.append(f"{obs['name']} {w}")
        if any('위험' in w for w in detect_abnormal(data)):
            danger_area.append(f"{obs['name']} 출항 금지")
    return render_template('mainPage.html',
                           warning=warning_msg,
                           danger_area=danger_area)

# ========= Warning/Danger API =========
@app.route('/api/warning')
def api_warning():
    msgs = []
    for obs in ObsCode:
        for w in detect_abnormal(get_obs_data(obs, url, ServiceKey)):
            msgs.append(f"{obs['name']} {w}")
    return jsonify({'warning': msgs})

@app.route('/api/danger_area')
def api_danger_area():
    msgs = []
    for obs in ObsCode:
        if any('위험' in w for w in detect_abnormal(get_obs_data(obs, url, ServiceKey))):
            msgs.append(f"{obs['name']} 출항 금지")
    return jsonify({'danger_area': msgs})

# ========= 상세 페이지 =========
@app.route('/incheon')
def incheon_detail():
    data = get_obs_data({'code':'DT_0011','name':'인천'}, url, ServiceKey)
    return render_template('incheon.html',
                           tide_level   = data.get('tide_level',0),
                           wind_speed   = data.get('wind_speed',0),
                           current_speed= data.get('current_speed',0))

@app.route('/taean')
def taean_detail():
    data = get_obs_data({'code':'DT_0025','name':'태안'}, url, ServiceKey)
    return render_template('taean.html',
                           tide_level   = data.get('tide_level',0),
                           wind_speed   = data.get('wind_speed',0),
                           current_speed= data.get('current_speed',0))

@app.route('/tongyeong')
def tongyeong_detail():
    data = get_obs_data({'code':'DT_0040','name':'통영'}, url, ServiceKey)
    return render_template('tongyeong.html',
                           tide_level   = data.get('tide_level',0),
                           wind_speed   = data.get('wind_speed',0),
                           current_speed= data.get('current_speed',0))

@app.route('/yeosu')
def yeosu_detail():
    data = get_obs_data({'code':'DT_0041','name':'여수'}, url, ServiceKey)
    return render_template('yeosu.html',
                           tide_level   = data.get('tide_level',0),
                           wind_speed   = data.get('wind_speed',0),
                           current_speed= data.get('current_speed',0))

@app.route('/uljin')
def uljin_detail():
    data = get_obs_data({'code':'DT_0036','name':'울진'}, url, ServiceKey)
    return render_template('uljin.html',
                           tide_level   = data.get('tide_level',0),
                           wind_speed   = data.get('wind_speed',0),
                           current_speed= data.get('current_speed',0))

# ========= OBS MAP =========
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
              수온: {show_value(data.get('water_temp', ''))} ℃<br>
              기온: {show_value(data.get('air_temp', ''))} ℃<br>
              기압: {show_value(data.get('air_press', ''))} hPa<br>
              풍속: {show_value(data.get('wind_speed', ''))} m/s<br>
              조위: {show_value(data.get('tide_level', ''))} cm<br>
              유속: {show_value(data.get('current_speed', ''))} m/s
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
                수온: {show_value(data.get('water_temp', ''))} ℃<br>
                기온: {show_value(data.get('air_temp', ''))} ℃<br>
                기압: {show_value(data.get('air_press', ''))} hPa<br>
                풍속: {show_value(data.get('wind_speed', ''))} m/s<br>
                유속: {show_value(data.get('current_speed', ''))} cm/s
                """
            folium.Marker(
                location=[lat, lon], tooltip=popup,
                icon=folium.Icon(icon='star', prefix='fa', color='blue')
            ).add_to(m)
        except Exception as e:
            print(f'부이 {name} 위치 정보 없음: {e}')
    html = m._repr_html_()
    return html

# ========= WIND/TIDE API =========
@app.route('/winddata')
def winddata():
    names = ['인천','통영','태안','여수','울진']
    return jsonify([{
        'name': obs['name'],
        'wind_speed': get_obs_data(obs, url, ServiceKey).get('wind_speed', 0)
    } for obs in ObsCode if obs['name'] in names])

@app.route('/tidedata')
def tidedata():
    names = ['인천','통영','태안','여수','울진']
    return jsonify([{
        'name': obs['name'],
        'tide_level': get_obs_data(obs, url, ServiceKey).get('tide_level', 0)
    } for obs in ObsCode if obs['name'] in names])

# ========= 그래프 엔드포인트 (태안만) =========
@app.route('/taean/graph.png')
def taean_graph():
    col       = request.args.get('col', 'sea_high')
    start_str = request.args.get('start', '2025-05-31 21:00:00')
    df_real   = pd.concat([df4, df5])
    return send_file(plot_graph(df_real, df6, col, start_str),
                     mimetype='image/png')

def plot_graph(df_real, df_pred, col, start_str):
    start = pd.to_datetime(start_str)
    end   = start + pd.Timedelta(hours=6)
    df_r  = df_real[(df_real['datetime'] >= start) & (df_real['datetime'] < end)]
    df_p  = df_pred[(df_pred['datetime'] >= start) & (df_pred['datetime'] < end)]

    plt.figure(figsize=(18,8), facecolor='#eaf3fb')
    ax = plt.gca()
    if not df_r.empty:
        ax.plot(df_r['datetime'], df_r[col],
                color='#2577e3', linewidth=4, marker='o', markersize=9, alpha=0.97)
    if not df_p.empty:
        ax.plot(df_p['datetime'], df_p[col],
                color='#ff8a57', linewidth=4, marker='o', markersize=9, linestyle='--', alpha=0.88)

    june = pd.Timestamp('2025-06-01')
    if (not df_r.empty and not df_p.empty and
        (df_r['datetime'] < june).any() and (df_p['datetime'] >= june).any()):
        ax.axvline(june, color='#888', linestyle='--', linewidth=2.6, alpha=0.72)

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

# ========= 차트 데이터 JSON API (나머지 지역들) =========
@app.route('/api/incheon_chart_data')
def incheon_chart_data():
    obs_df = pd.read_csv('./static/finalData/InCheon_05.csv')
    pred_df = pd.read_csv('../pred/this_InCheon_06.csv')

    def parse(df):
        df['datetime'] = pd.to_datetime(df['datetime']).dt.strftime('%Y-%m-%dT%H:%M:%S')
        return df[['datetime', 'sea_high', 'wind_speed', 'pressure', 'sea_speed']].dropna()

    obs = parse(obs_df)
    pred = parse(pred_df)

    return jsonify({
        'observed': obs.to_dict(orient='records'),
        'predicted': pred.to_dict(orient='records')
    })

@app.route('/api/yeosu_chart_data')
def yeosu_chart_data():
    obs_df = pd.read_csv('./static/finalData/Yeosu_05.csv')
    pred_df = pd.read_csv('../pred/this_Yeosu_06.csv')

    def parse(df):
        df['datetime'] = pd.to_datetime(df['datetime']).dt.strftime('%Y-%m-%dT%H:%M:%S')
        return df[['datetime', 'sea_high', 'wind_speed', 'pressure', 'sea_speed']].dropna()

    obs = parse(obs_df)
    pred = parse(pred_df)

    return jsonify({
        'observed': obs.to_dict(orient='records'),
        'predicted': pred.to_dict(orient='records')
    })

@app.route('/api/tongyeong_chart_data')
def tongyeong_chart_data():
    obs_df = pd.read_csv('./static/finalData/TongYeong_05.csv')
    pred_df = pd.read_csv('../pred/this_TongYeong_06.csv')

    def parse(df):
        df['datetime'] = pd.to_datetime(df['datetime']).dt.strftime('%Y-%m-%dT%H:%M:%S')
        return df[['datetime', 'sea_high', 'wind_speed', 'pressure', 'sea_speed']].dropna()

    obs = parse(obs_df)
    pred = parse(pred_df)

    return jsonify({
        'observed': obs.to_dict(orient='records'),
        'predicted': pred.to_dict(orient='records')
    })

@app.route('/api/uljin_chart_data')
def uljin_chart_data():
    obs_df = pd.read_csv('./static/finalData/Uljin_05.csv')
    pred_df = pd.read_csv('../pred/this_Uljin_06.csv')

    def parse(df):
        df['datetime'] = pd.to_datetime(df['datetime']).dt.strftime('%Y-%m-%dT%H:%M:%S')
        return df[['datetime', 'sea_high', 'wind_speed', 'pressure', 'sea_speed']].dropna()

    obs = parse(obs_df)
    pred = parse(pred_df)

    return jsonify({
        'observed': obs.to_dict(orient='records'),
        'predicted': pred.to_dict(orient='records')
    })

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
