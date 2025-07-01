from flask import Flask, render_template, jsonify
import random
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    # 실시간 데이터 생성 예시
    value = random.randint(1, 100)
    timestamp = int(time.time())
    return jsonify({'x': timestamp, 'y': value})

if __name__ == '__main__':
    app.run(debug=True)
