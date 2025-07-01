import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, mean_absolute_error
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
import joblib

# 1. 데이터 불러오기 및 합치기
file_list = [
    './data/Uljin_04.csv', './data/Uljin_05.csv',
    './data/Yeosu_04.csv', './data/Yeosu_05.csv',
    './data/InCheon_04.csv', './data/InCheon_05.csv',
    './data/Taean_04.csv', './data/Taean_05.csv',
    './data/TongYeong_04.csv', './data/TongYeong_05.csv'
]
df_all = pd.concat([pd.read_csv(f) for f in file_list], ignore_index=True)
print("전체 컬럼:", df_all.columns.tolist())

# 2. X, y 분리 (sea_dir_s 포함!)
X = df_all[['salt', 'wind_dir', 'temp', 'sea_dir_s', 'sea_dir_i', 'sea_temp']].copy()
y = df_all[['sea_high', 'wind_speed', 'pressure', 'sea_speed']]

# 3. 방향 컬럼(LabelEncoder) → fit된 인코더 저장
encoders = {}
for col in ['wind_dir', 'sea_dir_i', 'sea_dir_s']:
    X[col] = X[col].fillna('Unknown').astype(str)
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col])
    encoders[col] = le  # fit된 인코더 저장

# 4. train/test 분할
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 5. 정규화 (입력값만)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)

# 6. 딥러닝 모델 설계 (회귀, 출력 4개)
model = Sequential([
    Dense(128, input_shape=(X_train_scaled.shape[1],), activation='relu'),
    BatchNormalization(),
    Dropout(0.3),
    Dense(64, activation='relu'),
    BatchNormalization(),
    Dropout(0.3),
    Dense(32, activation='relu'),
    BatchNormalization(),
    Dropout(0.2),
    Dense(4, activation='linear')  # 4개 연속값 예측
])
model.compile(optimizer='adam', loss='mse', metrics=['mae'])

# # 7. 학습
# model.fit(
#     X_train_scaled, y_train,
#     epochs=100,
#     batch_size=32,
#     validation_data=(X_val_scaled, y_val),
#     verbose=2
# )

# 7. 학습
from tensorflow.keras.callbacks import EarlyStopping
early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

model.fit(
    X_train_scaled, y_train,
    epochs=200,  # 넉넉하게!
    batch_size=64,
    validation_data=(X_val_scaled, y_val),
    callbacks=[early_stop],
    verbose=2
)

# 8. 회귀 예측 결과 확인
y_val_pred = model.predict(X_val_scaled)
print("\n=== 검증 데이터 성능 ===")
print("평균절대오차(MAE):", mean_absolute_error(y_val, y_val_pred))
print("평균제곱오차(MSE):", mean_squared_error(y_val, y_val_pred))

# ⬇️ 여기부터 컬럼별 MAE/평균/비율 출력!
for i, col in enumerate(y.columns):
    mae = mean_absolute_error(y_val[col], y_val_pred[:, i])
    avg = y_val[col].mean()
    print(f"{col}: 평균={avg:.2f}, MAE={mae:.2f}, 상대오차={mae/avg*100:.2f}%")

# 9. 모델, 스케일러, 인코더 모두 저장 (실전 서비스처럼)
model.save('Data_can_sail_model.h5')
joblib.dump(scaler, 'Data_scaler.pkl')
joblib.dump(encoders, 'Data_encoders.pkl')
print("\n✅ 모델/스케일러/인코더 저장 완료")

# 10. (실전) 새로운 6월 데이터 예측 코드 예시 (필요시 사용)
'''
# === 6월 예측 예시 ===
df_june = pd.read_csv('./data/Yeosu_06.csv')
X_june = df_june[['salt', 'wind_dir', 'temp', 'sea_dir_s', 'sea_dir_i', 'sea_temp']].copy()
# 저장한 인코더 사용
encoders = joblib.load('Data_encoders.pkl')
for col in ['wind_dir', 'sea_dir_i', 'sea_dir_s']:
    X_june[col] = X_june[col].fillna('Unknown').astype(str)
    # transform만 사용 (신규 라벨 나오면 예외처리 필요)
    X_june[col] = encoders[col].transform(X_june[col])
scaler = joblib.load('Data_scaler.pkl')
X_june_scaled = scaler.transform(X_june)
model = load_model('Data_can_sail_model.h5')
pred = model.predict(X_june_scaled)
df_june[['sea_high_pred', 'wind_speed_pred', 'pressure_pred', 'sea_speed_pred']] = pred
print(df_june[['sea_high_pred', 'wind_speed_pred', 'pressure_pred', 'sea_speed_pred']])
'''


