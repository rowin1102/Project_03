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
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False

    # 데이터 로드
    final_data = pd.read_csv('../finalData/InCheon_05.csv').dropna(subset=['sea_high'])
    pred_data = pd.read_csv('../pred/this_InCheon_06.csv').dropna(subset=['sea_high'])

    # datetime 컬럼 생성
    final_data['datetime'] = pd.date_range(start='2025-05-31 00:00', periods=len(final_data), freq='10min')
    pred_data['datetime'] = pd.date_range(start='2025-06-01 00:00', periods=len(pred_data), freq='10min')

    graph_start = datetime(2025, 5, 31, 0, 0)      # 전체 가능한 시작 시간
    graph_end = datetime(2025, 6, 1, 23, 50)       # 전체 가능한 끝 시간
    transition_time = datetime(2025, 6, 1, 0, 0)   # 5월->6월 전환 시점
    window_hours = 4                                # 표시 시간 길이

    # 쿼리 파라미터로 받은 시작 시간, 없으면 기본값
    start_str = request.args.get('start', '2025-05-31 22:00')
    start_time = datetime.strptime(start_str, '%Y-%m-%d %H:%M')
    end_time = start_time + timedelta(hours=window_hours)

    # 5월 31일 전체 데이터 (회색 실선)
    may_start = datetime(2025, 5, 31, 0, 0)
    may_end = datetime(2025, 5, 31, 23, 59, 59)
    may_data_full = final_data[(final_data['datetime'] >= may_start) & (final_data['datetime'] <= may_end)]

    # 5월 현재 구간 실선 (표시 구간은 end_time이 transition_time 넘지 않도록)
    may_slice_end = min(end_time, transition_time)
    final_slice = final_data[(final_data['datetime'] >= start_time) & (final_data['datetime'] < may_slice_end)]

    # 6월 현재 구간 점선 (start_time이 transition_time 이상일 때만)
    pred_slice_start = max(start_time, transition_time)
    pred_slice = pred_data[(pred_data['datetime'] >= pred_slice_start) & (pred_data['datetime'] < end_time)]

    # 그래프 그리기
    fig, ax = plt.subplots(figsize=(14, 6))

    # 5월 전체 데이터 회색 실선
    ax.plot(may_data_full['datetime'], may_data_full['sea_high'], color='gray', linestyle='-', label='5월 31일 전체 데이터')

    # 5월 현재 구간 파란 실선, 굵게 강조
    if not final_slice.empty:
        ax.plot(final_slice['datetime'], final_slice['sea_high'], 'b-', label='5월 실측 (표시 구간)', linewidth=3)

    # 6월 현재 구간 빨간 점선 유지
    if not pred_slice.empty:
        ax.plot(pred_slice['datetime'], pred_slice['sea_high'], 'r--', label='6월 예측 (표시 구간)', linewidth=2)

    # 전환 시점 세로 검정 점선
    if start_time <= transition_time <= end_time:
        ax.axvline(x=transition_time, color='black', linestyle='--', linewidth=2, label='전환 시점 (6월 1일 00:00)')

    # 축 설정 및 스타일 개선
    ax.set_xlim(start_time, end_time)
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=20))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(100))

    ax.set_xlabel('시간', fontsize=14)
    ax.set_ylabel('조위 (cm)', fontsize=14)
    ax.set_title(f'인천 조위 변화: {start_time.strftime("%m-%d %H:%M")} ~ {end_time.strftime("%m-%d %H:%M")}', fontsize=18, weight='bold')

    plt.xticks(rotation=45, fontsize=12)
    plt.yticks(fontsize=12)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

    # 범례 폰트 키우기
    ax.legend(fontsize=12)

    plt.tight_layout()

    # 이미지로 변환
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    # 이전/다음 1시간씩 이동
    prev_time = start_time - timedelta(hours=1)
    next_time = start_time + timedelta(hours=1)

    # 버튼 활성화 조건
    prev_start = prev_time.strftime('%Y-%m-%d %H:%M') if prev_time >= graph_start else None
    next_start = next_time.strftime('%Y-%m-%d %H:%M') if next_time + timedelta(hours=window_hours) <= graph_end else None

    return render_template('test.html',
                        graph_url=graph_url,
                        current_window=f"{start_time.strftime('%m-%d %H:%M')} ~ {end_time.strftime('%m-%d %H:%M')}",
                        prev_start=prev_start,
                        next_start=next_start)

@app.route('/test2', methods=['GET', 'POST'])
def test2():
    
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False

    final_data = pd.read_csv('../finalData/InCheon_05.csv').dropna(subset=['sea_high'])
    pred_data = pd.read_csv('../pred/this_InCheon_06.csv').dropna(subset=['sea_high'])

    final_data['datetime'] = pd.date_range(start='2025-05-31 00:00', periods=len(final_data), freq='10min')
    pred_data['datetime'] = pd.date_range(start='2025-06-01 00:00', periods=len(pred_data), freq='10min')

    graph_start = datetime(2025, 5, 31, 0, 0)      # 전체 가능한 시작 시간 (5월 31일 0시)
    graph_end = datetime(2025, 6, 1, 23, 50)       # 전체 가능한 끝 시간 (6월 1일 마지막 데이터 시간)
    transition_time = datetime(2025, 6, 1, 0, 0)
    window_hours = 4

    start_str = request.args.get('start', '2025-05-31 22:00')
    start_time = datetime.strptime(start_str, '%Y-%m-%d %H:%M')
    end_time = start_time + timedelta(hours=window_hours)

    # 5월 31일 전체 데이터 (회색 점선)
    may_start = datetime(2025, 5, 31, 0, 0)
    may_end = datetime(2025, 5, 31, 23, 59, 59)
    may_data_full = final_data[(final_data['datetime'] >= may_start) & (final_data['datetime'] <= may_end)]

    # 5월 실측 데이터 (현재 윈도우 내, end_time이 6월 1일 0시를 넘지 않게 제한)
    may_slice_end = min(end_time, transition_time)
    final_slice = final_data[(final_data['datetime'] >= start_time) & (final_data['datetime'] < may_slice_end)]

    # 6월 예측 데이터 (현재 윈도우 내, start_time이 6월 1일 0시 이상인 경우)
    pred_slice_start = max(start_time, transition_time)
    pred_slice = pred_data[(pred_data['datetime'] >= pred_slice_start) & (pred_data['datetime'] < end_time)]

    fig, ax = plt.subplots(figsize=(14, 6))

    # 5월 전체 회색 점선
    ax.plot(may_data_full['datetime'], may_data_full['sea_high'], color='gray', linestyle='--', label='5월 31일 전체 데이터')

    # 5월 현재 구간 실선
    if not final_slice.empty:
        ax.plot(final_slice['datetime'], final_slice['sea_high'], 'b-', label='5월 실측 (표시 구간)', linewidth=2)

    # 6월 현재 구간 점선
    if not pred_slice.empty:
        ax.plot(pred_slice['datetime'], pred_slice['sea_high'], 'r--', label='6월 예측 (표시 구간)', linewidth=2)

    # 5월과 6월 사이 전환 시점 세로 점선
    if start_time <= transition_time <= end_time:
        ax.axvline(x=transition_time, color='black', linestyle='--', linewidth=2, label='전환 시점 (6월 1일 00:00)')

    ax.set_xlim(start_time, end_time)
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=20))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(100))

    ax.set_xlabel('시간', fontsize=12)
    ax.set_ylabel('조위 (cm)', fontsize=12)
    ax.set_title(f'인천 조위 변화: {start_time.strftime("%m-%d %H:%M")} ~ {end_time.strftime("%m-%d %H:%M")}', fontsize=16)

    plt.xticks(rotation=45)
    ax.grid(True)
    ax.legend()
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    # 이전/다음 1시간씩 이동
    prev_time = start_time - timedelta(hours=1)
    next_time = start_time + timedelta(hours=1)

    # 이전/다음 버튼 활성화 조건 - 전체 데이터 범위 내에서만 이동 허용
    prev_start = prev_time.strftime('%Y-%m-%d %H:%M') if prev_time >= graph_start else None
    next_start = next_time.strftime('%Y-%m-%d %H:%M') if next_time + timedelta(hours=window_hours) <= graph_end else None

    return render_template('test2.html',
                           graph_url=graph_url,
                           current_window=f"{start_time.strftime('%m-%d %H:%M')} ~ {end_time.strftime('%m-%d %H:%M')}",
                           prev_start=prev_start,
                           next_start=next_start)


@app.route('/test3')
def test3():
    
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False

    # 데이터 로드
    final_data = pd.read_csv('../finalData/InCheon_05.csv').dropna(subset=['sea_high'])
    pred_data = pd.read_csv('../pred/this_InCheon_06.csv').dropna(subset=['sea_high'])

    # datetime 컬럼 생성
    final_data['datetime'] = pd.date_range(start='2025-05-31 00:00', periods=len(final_data), freq='10min')
    pred_data['datetime'] = pd.date_range(start='2025-06-01 00:00', periods=len(pred_data), freq='10min')

    # 그래프 표시 범위
    graph_start = datetime(2025, 5, 31, 22, 0)
    graph_end = datetime(2025, 6, 1, 2, 0)
    transition_time = datetime(2025, 6, 1, 0, 0)

    # 시각화 데이터 슬라이싱
    final_slice = final_data[(final_data['datetime'] >= graph_start) & (final_data['datetime'] < transition_time)]
    pred_slice = pred_data[(pred_data['datetime'] >= transition_time) & (pred_data['datetime'] <= graph_end)]

    # 그래프 생성
    fig, ax = plt.subplots(figsize=(14, 6))

    # 실측 데이터 (파란 선)
    if not final_slice.empty:
        ax.plot(final_slice['datetime'], final_slice['sea_high'], 'b-', label='실측 (5월)', linewidth=2)

    # 예측 데이터 (빨간 점선)
    if not pred_slice.empty:
        ax.plot(pred_slice['datetime'], pred_slice['sea_high'], 'r--', label='예측 (6월)', linewidth=2)

    # 전환 시점 세로 점선
    ax.axvline(x=transition_time, color='gray', linestyle='--', linewidth=2, label='전환 시점 (6월 1일 00:00)')

    # 축 설정
    ax.set_xlim(graph_start, graph_end)
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=20))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(100))

    # 제목, 레이블
    ax.set_title('인천 조위 변화 (2025-05-31 22:00 ~ 2025-06-01 02:00)', fontsize=16)
    ax.set_xlabel('시간', fontsize=12)
    ax.set_ylabel('조위 (cm)', fontsize=12)

    ax.legend()
    ax.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # 그래프 이미지를 base64로 변환
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return render_template('test3.html',
                           graph_url=graph_url,
                           current_window="2025-05-31 22:00 ~ 2025-06-01 02:00",
                           prev_start=None,
                           next_start=None)
    
@app.route('/test4')
def test4():
    # 폰트 설정
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False

    # 데이터 로드 및 전처리
    final_data = pd.read_csv('../finalData/InCheon_05.csv').dropna(subset=['sea_high'])
    pred_data = pd.read_csv('../pred/this_InCheon_06.csv').dropna(subset=['sea_high'])

    final_data['datetime'] = pd.date_range(start='2025-05-31 00:00', periods=len(final_data), freq='10min')
    pred_data['datetime'] = pd.date_range(start='2025-06-01 00:00', periods=len(pred_data), freq='10min')

    # 시각화 구간 설정
    graph_start = datetime(2025, 5, 31, 22, 0)
    graph_end = datetime(2025, 6, 1, 2, 0)
    transition_time = datetime(2025, 6, 1, 0, 0)

    # 슬라이싱
    final_slice = final_data[(final_data['datetime'] >= graph_start) & (final_data['datetime'] < transition_time)]
    pred_slice = pred_data[(pred_data['datetime'] >= transition_time) & (pred_data['datetime'] <= graph_end)]

    # 그래프 생성
    fig, ax = plt.subplots(figsize=(14, 6))

    if not final_slice.empty:
        ax.plot(final_slice['datetime'], final_slice['sea_high'], 'b-', label='실측 (5월 31일)', linewidth=2)

    if not pred_slice.empty:
        ax.plot(pred_slice['datetime'], pred_slice['sea_high'], 'r--', label='예측 (6월 1일)', linewidth=2)

    # 세로 점선 추가
    ax.axvline(x=transition_time, color='gray', linestyle='--', linewidth=2, label='전환 시점 (6월 1일 00:00)')

    # 축 설정
    ax.set_xlim(graph_start, graph_end)
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=20))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(100))

    # 제목 및 레이블
    ax.set_title('인천 조위 변화 (5월 31일 22시 ~ 6월 1일 2시)', fontsize=16)
    ax.set_xlabel('시간', fontsize=12)
    ax.set_ylabel('조위 (cm)', fontsize=12)

    plt.xticks(rotation=45)
    ax.grid(True)
    ax.legend()
    plt.tight_layout()

    # 이미지 변환
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return render_template('test4.html', graph_url=graph_url)
    #render_template('test4.html')

@app.route('/test5')
def test5():
    # 한글 폰트 설정
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False

    # 데이터 로드
    final_data = pd.read_csv('../finalData/InCheon_05.csv').dropna(subset=['sea_high'])
    pred_data = pd.read_csv('../pred/this_InCheon_06.csv').dropna(subset=['sea_high'])

    # datetime 컬럼 생성
    final_data['datetime'] = pd.date_range(start='2025-05-31 00:00', periods=len(final_data), freq='10min')
    pred_data['datetime'] = pd.date_range(start='2025-06-01 00:00', periods=len(pred_data), freq='10min')

    # 그래프 기본 범위 설정
    graph_start = datetime(2025, 5, 31, 22, 0)
    graph_end = datetime(2025, 6, 1, 2, 0)
    transition_time = datetime(2025, 6, 1, 0, 0)
    window_hours = 4  # 표시할 시간 구간 길이 (4시간)

    # 시작시간 파라미터 (없으면 기본값 5/31 22:00)
    start_str = request.args.get('start', graph_start.strftime('%Y-%m-%d %H:%M'))
    start_time = datetime.strptime(start_str, '%Y-%m-%d %H:%M')

    # 끝나는 시간
    end_time = start_time + timedelta(hours=window_hours)

    # 5월 데이터는 전체를 로드했으니 표시 구간에 맞춰 슬라이싱
    # 단, 5월 데이터는 5/31 00:00~5/31 22:00 이전 데이터도 다 가지고 있지만, 표시범위에 맞춰서 자름
    final_slice = final_data[(final_data['datetime'] >= start_time) & (final_data['datetime'] < min(end_time, transition_time))]

    # 6월 데이터는 6/1 00:00 이후 데이터만 사용 (전체 데이터에서 슬라이싱)
    pred_slice = pred_data[(pred_data['datetime'] >= max(start_time, transition_time)) & (pred_data['datetime'] < end_time)]

    # 그래프 생성
    fig, ax = plt.subplots(figsize=(14, 6))

    # 5월 실측 데이터 파란선
    if not final_slice.empty:
        ax.plot(final_slice['datetime'], final_slice['sea_high'], 'b-', label='실측 (5월)', linewidth=2)

    # 6월 예측 데이터 빨간 점선
    if not pred_slice.empty:
        ax.plot(pred_slice['datetime'], pred_slice['sea_high'], 'r--', label='예측 (6월)', linewidth=2)

    # 전환 시점 세로 점선
    if start_time <= transition_time <= end_time:
        ax.axvline(x=transition_time, color='gray', linestyle='--', linewidth=2, label='전환 시점 (6월 1일 00:00)')

    # 축 설정
    ax.set_xlim(start_time, end_time)
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=20))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(100))

    # 레이블 및 제목
    ax.set_xlabel('시간', fontsize=12)
    ax.set_ylabel('조위 (cm)', fontsize=12)
    ax.set_title(f'인천 조위 변화: {start_time.strftime("%m-%d %H:%M")} ~ {end_time.strftime("%m-%d %H:%M")}', fontsize=16)

    plt.xticks(rotation=45)
    ax.grid(True)
    ax.legend()
    plt.tight_layout()

    # 이미지 변환 (base64)
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    # 이전/다음 버튼 시간 계산 (1시간 단위)
    prev_time = start_time - timedelta(hours=1)
    next_time = start_time + timedelta(hours=1)

    # 범위 제한 (그래프 표시 구간 내)
    prev_start = prev_time.strftime('%Y-%m-%d %H:%M') if prev_time >= graph_start else None
    next_start = next_time.strftime('%Y-%m-%d %H:%M') if next_time <= graph_end else None

    return render_template('test5.html',
                           graph_url=graph_url,
                           current_window=f"{start_time.strftime('%m-%d %H:%M')} ~ {end_time.strftime('%m-%d %H:%M')}",
                           prev_start=prev_start,
                           next_start=next_start)    
    #return render_template("test5.html")

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