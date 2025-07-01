from flask import Flask, render_template, jsonify
from abnormal import detect_abnormal
from obs_data import get_obs_data
from obs_list import ObsCode

app = Flask(__name__)

url = 'http://www.khoa.go.kr/api/oceangrid/tideObsRecent/search.do'
ServiceKey = 'yw1Xau9HH4k4eQmO0r65AA=='


  
  
  
@app.route('/piechart')
def piechart():
   
    # 총합 저장
    totals = {
        'tide_level': 0,
        'wind_speed': 0,
        'current_speed': 0,
        'air_temp': 0,
        'air_press': 0,
        'water_temp': 0
    }

    # 한글 항목명
    labels_ko = {
        'tide_level': '조위',
        'wind_speed': '풍속',
        'current_speed': '유속',
        'air_temp': '기온',
        'air_press': '기압',
        'water_temp': '수온'
    }

    for obs in ObsCode:
        data = get_obs_data(obs, url, ServiceKey)
        for key in totals:
            if key in data:
                totals[key] += data[key]

    labels = [labels_ko[k] for k in totals]
    values = list(totals.values())
    colors = ['#4dd0e1', '#81c784', '#ffb74d', '#9575cd', '#f06292', '#90a4ae']

    return render_template('chart.html',
                           labels=labels,
                           values=values,
                           colors=colors)

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