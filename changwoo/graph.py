import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 데이터 읽기
df_may = pd.read_csv("./finalData/InCheon_05.csv", encoding="cp949")
df_june = pd.read_csv("./pred/this_InCheon_06.csv", encoding="cp949")

# 날짜 파싱
df_may['dt'] = pd.to_datetime(df_may['datetime'], errors='coerce')
df_june['dt'] = pd.to_datetime(df_june['datetime'], errors='coerce')

# sea_high 숫자 변환
df_may['sea_high'] = pd.to_numeric(df_may['sea_high'], errors='coerce')
df_june['sea_high'] = pd.to_numeric(df_june['sea_high'], errors='coerce')

# 구간 자르기
start_window = pd.Timestamp("2025-05-31 21:00")
end_window = pd.Timestamp("2025-06-01 03:00")
may31 = df_may[(df_may['dt'] >= start_window) & (df_may['dt'] < pd.Timestamp("2025-06-01 00:00"))]
june1 = df_june[(df_june['dt'] >= pd.Timestamp("2025-06-01 00:00")) & (df_june['dt'] <= end_window)]

# 그래프
plt.figure(figsize=(14, 5))
plt.plot(may31['dt'], may31['sea_high'], color='royalblue', linewidth=2, label='Actual (May 31)', linestyle='-')
plt.plot(june1['dt'], june1['sea_high'], color='orangered', linewidth=2, label='Prediction (June 1)', linestyle='--')
plt.axvline(x=pd.Timestamp("2025-06-01 00:00"), color='black', linestyle='--', linewidth=2, label="Boundary (06-01 00:00)")

plt.title("Sea Level (조위) Zoomed: 2025-05-31 21:00 ~ 2025-06-01 03:00")
plt.xlabel("Datetime (MM-DD HH)")
plt.ylabel("Sea High (조위, m)")

ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H시"))
ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
plt.xticks(rotation=45, fontsize=8)

plt.legend()
plt.grid(True, linestyle=':', linewidth=0.7)
plt.tight_layout()
plt.show()
