from flask import Flask, render_template, jsonify
from abnormal import detect_abnormal
from obs_data import get_obs_data

app = Flask(__name__)

url = 'http://www.khoa.go.kr/api/oceangrid/tideObsRecent/search.do'
ServiceKey = 'c2jVwblwmcHB5tOEWxEjbg=='

ObsCode = [
    {'name' : '인천', 'code' : 'DT_0001'},
    {'name' : '통영', 'code' : 'DT_0002'},
    {'name' : '태안', 'code' : 'DT_0050'},
    {'name' : '여수', 'code' : 'DT_0016'},
    {'name' : '울진', 'code' : 'DT_0011'},
]

@app.route('/')
def dashboard():
  warning_msg = []
  for obs in ObsCode:
    data = get_obs_data(obs, url, ServiceKey)
    warning = detect_abnormal(data)
    for w in warning:
      warning_msg.append(f"{obs['name']} {w} 경고") 
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
      warning_msg.append(f"{obs['name']} {w} 경고") 
  return jsonify({'warning' : warning_msg})

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8080, debug=True)