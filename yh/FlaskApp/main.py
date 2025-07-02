from flask import Flask, render_template, jsonify
from abnormal import detect_abnormal
from obs_data import get_obs_data
from obs_list import ObsCode

app = Flask(__name__)

url = 'http://www.khoa.go.kr/api/oceangrid/tideObsRecent/search.do'
ServiceKey = 'yw1Xau9HH4k4eQmO0r65AA=='

  
@app.route('/piechart2')
def piechart2():
    return render_template('chart05.html')  # 아래 HTML 파일 렌더링

@app.route('/winddata')
def winddata():
    target_names = ['인천', '통영', '태안', '여수', '울진']
    selected_obs = [obs for obs in ObsCode if obs['name'] in target_names]

    tide_data = []
    for obs in selected_obs:
        result = get_obs_data(obs, url, ServiceKey)  # 최신 데이터 호출
        tide_level = result.get('tide_level', 0) if result else 0
        tide_data.append({'name': obs['name'], 'tide_level': tide_level})

    return jsonify(tide_data)
    
@app.route('/')
def dashboard():
  warning_msg = []
  for obs in ObsCode:
    data = get_obs_data(obs, url, ServiceKey)
    warning = detect_abnormal(data)
    for w in warning:
      warning_msg.append(f"{obs['name']} {w}") 
  return render_template('mainPage.html', warning=warning_msg)
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
      danger_msg.append(obs['name'])
  return jsonify({'danger_area' : danger_msg})

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8080, debug=True)