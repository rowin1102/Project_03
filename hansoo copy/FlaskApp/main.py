from flask import Flask, render_template, jsonify
from abnormal import detect_abnormal
from obs_data import get_obs_data
from obs_list import ObsCode

app = Flask(__name__)

url = 'http://www.khoa.go.kr/api/oceangrid/tideObsRecent/search.do'
ServiceKey = 'yw1Xau9HH4k4eQmO0r65AA=='

@app.route('/piechart')
def piechart():
    target_ports = ['부산', '여수', '태안', '통영', '울진']
    filter_obs = [obs for obs in ObsCode if obs['name'] in target_ports]
    datas = []
    for obs in filter_obs:
        d = get_obs_data(obs, url, ServiceKey)
        if d: datas.append(d)
  
    # 풍속 분포: 약풍/미풍/강풍 기준 분류
    cat = {'약풍 (<3.3m/s)':0, '미풍 (3.3~6.6m/s)':0, '강풍 (>6.6m/s)':0}
    for d in datas:
        ws = d['wind_speed']
        if ws < 3.3:
            cat['약풍 (<3.3m/s)'] += 1
        elif ws < 6.6:
            cat['미풍 (3.3~6.6m/s)'] += 1
        else:
            cat['강풍 (>6.6m/s)'] += 1

    labels = list(cat.keys())
    values = list(cat.values())
    colors = ['#81c784', '#ffb74d', '#e57373']

    return render_template('chart.html',
                           datas=datas,
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