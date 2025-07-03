import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from matplotlib.widgets import Button

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 로드
final_data = pd.read_csv('finalData/InCheon_05.csv')
pred_data = pd.read_csv('pred/this_InCheon_06.csv')

# datetime 컬럼 생성
final_data['datetime'] = pd.date_range(start='2024-05-31 00:00', periods=len(final_data), freq='10min')
pred_data['datetime'] = pd.date_range(start='2024-06-01 00:00', periods=len(pred_data), freq='10min')

# 숫자 컬럼 찾기
def find_numeric_column(df):
    for col in df.columns:
        if col != 'datetime' and pd.api.types.is_numeric_dtype(df[col]):
            return col
    return df.columns[0]

value_col_final = find_numeric_column(final_data)
value_col_pred = find_numeric_column(pred_data)

# 범위 설정
start_time = datetime(2024, 5, 31, 0, 0)
end_time = datetime(2024, 6, 1, 23, 59)
window_hours = 6
current_start = start_time
current_end = current_start + timedelta(hours=window_hours)

# 필터 마스크
final_mask = final_data['datetime'] <= datetime(2024, 5, 31, 23, 59)
pred_mask = pred_data['datetime'] >= datetime(2024, 6, 1, 0, 0)
transition_time = datetime(2024, 6, 1, 0, 0)

# y축 범위 계산
y_min = min(final_data[value_col_final].min(), pred_data[value_col_pred].min())
y_max = max(final_data[value_col_final].max(), pred_data[value_col_pred].max())

# 그래프 및 UI 영역 설정
fig, ax = plt.subplots(figsize=(14, 8))
plt.subplots_adjust(top=0.85, bottom=0.15)

# 상단 제목
fig.suptitle("인천 조위 데이터", fontsize=16, fontweight='bold', y=0.96)

# 버튼 및 텍스트 UI 축 생성 (왼쪽으로 이동)
ax_btn_left = plt.axes([0.70, 0.92, 0.04, 0.04])  # 좌측 버튼
btn_left = Button(ax_btn_left, '◀')
btn_left.label.set_fontsize(12)

ax_text = plt.axes([0.75, 0.92, 0.10, 0.04])  # 날짜/시간 텍스트 (버튼 바로 옆)
ax_text.axis('off')
text_obj = ax_text.text(0.5, 0.5, '', ha='center', va='center', fontsize=11)

ax_btn_right = plt.axes([0.86, 0.92, 0.04, 0.04])  # 우측 버튼
btn_right = Button(ax_btn_right, '▶')
btn_right.label.set_fontsize(12)

def plot_graph():
    ax.clear()
    ax.plot(final_data[final_mask]['datetime'], final_data[final_mask][value_col_final],
            'b-', linewidth=2, label='5월 31일', marker='o', markersize=3, markevery=1)
    ax.plot(pred_data[pred_mask]['datetime'], pred_data[pred_mask][value_col_pred],
            'r--', linewidth=2, label='6월 1일', alpha=0.8)
    ax.axvline(x=transition_time, color='black', linestyle=':', alpha=0.8, linewidth=2)

    ax.set_xlim(current_start, current_end)
    ax.set_ylim(y_min * 0.95, y_max * 1.15)
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.set_ylabel('조위 (cm)')
    ax.set_xlabel('시간 (시)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    text_obj.set_text(f"{current_start.strftime('%m/%d %H:%M')} ~ {current_end.strftime('%H:%M')}")
    fig.canvas.draw()

def move_left(event):
    global current_start, current_end
    if current_start <= start_time:
        return
    current_start -= timedelta(hours=1)
    current_end -= timedelta(hours=1)
    plot_graph()

def move_right(event):
    global current_start, current_end
    if current_end >= end_time:
        return
    current_start += timedelta(hours=1)
    current_end += timedelta(hours=1)
    plot_graph()

btn_left.on_clicked(move_left)
btn_right.on_clicked(move_right)

plot_graph()
plt.show()
