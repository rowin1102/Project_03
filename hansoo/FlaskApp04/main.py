from flask import Flask, render_template, jsonify
import json, json, folium
from abnormal import detect_abnormal
from obs_data import get_obs_data
from obs_list import ObsCode

import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import matplotlib.dates as mdates
import numpy as np
from scipy.interpolate import make_interp_spline
import matplotlib.ticker as ticker  # ← 추가
from datetime import datetime, timedelta
import numpy as np

from matplotlib import ticker, dates as mdates
from scipy.interpolate import interp1d
import io
from flask import Flask, request, render_template


app = Flask(__name__)

url = 'http://www.khoa.go.kr/api/oceangrid/tideObsRecent/search.do'
#ServiceKey = 'c2jVwblwmcHB5tOEWxEjbg=='
#ServiceKey = 'yw1Xau9HH4k4eQmO0r65AA=='
ServiceKey = 'uHRQY9ctKuLtELm0nTRpg=='

with open('./observatory/jo.json', encoding='utf-8') as f:
    ObsCode_json = json.load(f)
with open('./observatory/bui.json', encoding='utf-8') as f:
    BuiCode_json = json.load(f)

@app.route('/test1')
def test1():
    #df1 = pd.read_csv('../finalData/InCheon_05.csv', encoding='utf-8')
    #df2 = pd.read_csv('../pred/this_InCheon_06.csv', encoding='utf-8')

    # sea_high 컬럼 가져오기 + 소수점 제거 (정수형 변환)
    #series1 = df1['sea_high'].astype(int)
    #series2 = df2['sea_high'].astype(int)
    

    # 한글 폰트 설정
    plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows
    plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

    # 데이터 로드
    final_data = pd.read_csv('../finalData/InCheon_05.csv')
    pred_data = pd.read_csv('../pred/this_InCheon_06.csv')

    print("Final data columns:", final_data.columns.tolist())
    print(final_data.head())
    print(final_data.info())

    print("Pred data columns:", pred_data.columns.tolist())
    print(pred_data.head())
    print(pred_data.info())

    # sea_high 컬럼 숫자 타입 변환 및 결측치 확인
    if 'sea_high' not in final_data.columns:
        return "final_data에 sea_high 컬럼이 없습니다."

    if final_data['sea_high'].isnull().any():
        print("final_data sea_high에 결측치가 있습니다. 결측치 처리 필요")
        final_data = final_data.dropna(subset=['sea_high'])

    # 시간 컬럼 생성 (10분 간격)
    final_data = final_data.reset_index(drop=True)
    pred_data = pred_data.reset_index(drop=True)

    final_data['time'] = pd.date_range(start='2024-05-31 00:00', periods=len(final_data), freq='10min')
    pred_data['time'] = pd.date_range(start='2024-06-01 00:00', periods=len(pred_data), freq='10min')

    # value_col_final, value_col_pred는 'sea_high' 로 고정 (원본 데이터가 sea_high라 가정)
    value_col_final = 'sea_high'
    value_col_pred = 'sea_high'

    # 한글 폰트 설정
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False

    # 그래프 그리기
    fig, ax = plt.subplots(figsize=(14, 8))

    final_mask = final_data['time'] <= datetime(2024, 5, 31, 23, 59)
    ax.plot(final_data.loc[final_mask, 'time'], final_data.loc[final_mask, value_col_final],
            'b-', linewidth=2, marker='o', markersize=3, markevery=1, label='인천 5월 31일')

    pred_mask = pred_data['time'] >= datetime(2024, 6, 1, 0, 0)
    ax.plot(pred_data.loc[pred_mask, 'time'], pred_data.loc[pred_mask, value_col_pred],
            'r--', linewidth=2, label='인천 6월 1일', alpha=0.8)

    transition_time = datetime(2024, 6, 1, 0, 0)
    ax.axvline(x=transition_time, color='black', linestyle=':', alpha=0.8, linewidth=2)

    y_max = max(final_data[value_col_final].max(), pred_data[value_col_pred].max())
    y_min = min(final_data[value_col_final].min(), pred_data[value_col_pred].min())

    ax.text(datetime(2024, 5, 31, 12, 0), y_max * 1.05, '5/31', ha='center', va='bottom', fontsize=14, fontweight='bold')
    ax.text(datetime(2024, 6, 1, 12, 0), y_max * 1.05, '6/1', ha='center', va='bottom', fontsize=14, fontweight='bold')

    ax.set_xlim(datetime(2024, 5, 31, 0, 0), datetime(2024, 6, 1, 23, 59))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H'))

    ax.yaxis.set_major_locator(ticker.MultipleLocator(100))

    ax.set_xlabel('시간 (시)', fontsize=12)
    ax.set_ylabel('조위 (cm)', fontsize=12)
    ax.set_title('인천 조위 데이터', fontsize=16, pad=25, fontweight='bold')

    ax.legend(loc='upper left', fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)

    ax.set_ylim(y_min * 0.95, y_max * 1.15)

    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)

    return render_template('test.html', graph_url=graph_url)
    #return render_template('test.html')

@app.route('/test2', methods=['GET', 'POST'])
def test2():
    
    # 데이터 불러오기
    df1 = pd.read_csv('../finalData/InCheon_05.csv', encoding='utf-8')
    df2 = pd.read_csv('../pred/this_InCheon_06.csv', encoding='utf-8')

    # sea_high 추출
    series1 = df1['sea_high']
    series2 = df2['sea_high']

    # 한글 폰트 설정 (Windows)
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False

    # 데이터 로드 및 전처리
    final_data = pd.read_csv('../finalData/InCheon_05.csv')
    pred_data = pd.read_csv('../pred/this_InCheon_06.csv')

    # sea_high 결측치 제거
    final_data = final_data.dropna(subset=['sea_high']).reset_index(drop=True)
    pred_data = pred_data.dropna(subset=['sea_high']).reset_index(drop=True)

    # 시간 컬럼 생성 (10분 간격)
    final_data['time'] = pd.date_range(start='2024-05-31 00:00', periods=len(final_data), freq='10min')
    pred_data['time'] = pd.date_range(start='2024-06-01 00:00', periods=len(pred_data), freq='10min')

    # 전체 데이터 합치기(시간순 정렬)
    data = pd.concat([final_data, pred_data], ignore_index=True).sort_values('time').reset_index(drop=True)

    # 시작 시간: POST로 받거나 기본값 설정
    if request.method == 'POST' and 'start_time' in request.form:
        try:
            start_time = datetime.strptime(request.form['start_time'], '%Y-%m-%d %H:%M')
        except ValueError:
            start_time = datetime(2024, 5, 31, 0, 0)
    else:
        start_time = datetime(2024, 5, 31, 0, 0)

    # 1시간 구간 설정
    end_time = start_time + timedelta(hours=1)

    # 해당 구간 데이터 필터링
    window_data = data[(data['time'] >= start_time) & (data['time'] <= end_time)]

    # 그래프 그리기
    fig, ax = plt.subplots(figsize=(14, 6))

    # final_data 구간 (파란색, 원형 마커)
    mask_final = window_data['time'] < datetime(2024, 6, 1, 0, 0)
    ax.plot(window_data.loc[mask_final, 'time'], window_data.loc[mask_final, 'sea_high'],
            'bo-', label='인천 5월 31일 (관측)', markersize=4)

    # pred_data 구간 (빨간색, 사각형 마커)
    mask_pred = window_data['time'] >= datetime(2024, 6, 1, 0, 0)
    ax.plot(window_data.loc[mask_pred, 'time'], window_data.loc[mask_pred, 'sea_high'],
            'rs--', label='인천 6월 1일 (예측)', markersize=4, alpha=0.8)

    # 날짜 구분선
    ax.axvline(x=datetime(2024, 6, 1, 0, 0), color='black', linestyle=':', linewidth=2, alpha=0.7)

    # 축 설정
    ax.set_xlim(start_time, end_time)
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=10))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    # Y축 범위 설정 (10% 여유)
    y_max = window_data['sea_high'].max()
    y_min = window_data['sea_high'].min()
    ax.set_ylim(y_min * 0.9, y_max * 1.1)

    ax.set_xlabel('시간 (10분 단위)')
    ax.set_ylabel('조위 (cm)')
    ax.set_title(f'{start_time.strftime("%Y-%m-%d %H:%M")} ~ {end_time.strftime("%H:%M")} 인천 조위 데이터')

    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='upper left', fontsize=11)

    plt.tight_layout()

    # 이미지 변환
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)

    # 이전/다음 시간 계산 (1시간씩 이동)
    prev_time = (start_time - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')
    next_time = (start_time + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')

    return render_template('test.html',
                           graph_url=graph_url,
                           prev_time=prev_time,
                           next_time=next_time)

@app.route('/test3')
def test3():
    
    # # CSV 불러오기
    # df1 = pd.read_csv('../finalData/InCheon_05.csv', encoding='utf-8')
    # df2 = pd.read_csv('../pred/this_InCheon_06.csv', encoding='utf-8')

    # # sea_high 값 추출
    # real = df1['sea_high'].tolist()
    # pred = df2['sea_high'].tolist()
    # all_values = real + pred

    # # 시간 생성: 1시간 간격
    # start_time = datetime(2024, 6, 1, 0, 0)
    # times = [(start_time + timedelta(hours=i)).strftime('%Y-%m-%d %H:%M') for i in range(len(all_values))]
    
    # return render_template('test3.html', times=times, values=all_values)
    return render_template('test3.html')

@app.route('/data')
def get_data():
    df1 = pd.read_csv('../finalData/InCheon_05.csv', encoding='utf-8')
    df2 = pd.read_csv('../pred/this_InCheon_06.csv', encoding='utf-8')
    
    data = {
        'df1': df1.iloc[:, 1].tolist(),
        'df2': df2.iloc[:, 1].tolist()
    }
    return jsonify(data)
    

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

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8080, debug=True)