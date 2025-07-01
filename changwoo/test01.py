import os
import pandas as pd
import numpy as np
import joblib
from tensorflow.keras.models import load_model
from sklearn.metrics import accuracy_score, classification_report

regions = ['InCheon', 'Yeosu', 'Tongyeong', 'Taean', 'Uljin']
input_cols = ['sea_high', 'salt', 'wind_speed', 'wind_dir', 'temp', 'pressure',
              'sea_speed', 'sea_dir_s', 'sea_dir_i', 'sea_temp']
bins_num = 3

predict_dir = './changwoo/predict'
os.makedirs(predict_dir, exist_ok=True)

summary_path = './changwoo/predict/results_summary.txt'
# 기존 요약 파일 있으면 초기화
if os.path.exists(summary_path):
    os.remove(summary_path)

def save_summary_log(region, item, y_true, y_pred, save_path=summary_path):
    acc = accuracy_score(y_true, y_pred)
    report = classification_report(y_true, y_pred, digits=4, zero_division=0)
    log = f"\n--- [{region} / {item}] ---\n"
    log += f"분류 정확도 (accuracy): {acc:.4f}\n"
    log += f"{report}\n"

    with open(save_path, 'a', encoding='utf-8') as f:
        f.write(log)
    print(log)

for region in regions:
    print(f"\n=== {region} 2024-06 예측 시작 ===")
    test_path  = f'./finalData/{region}_06.csv'
    try:
        test_df = pd.read_csv(test_path)
    except Exception as e:
        print(f"[{region}] 테스트 데이터 로드 실패: {e}")
        continue

    # 방향 변수 라벨 인코딩
    for col in ['wind_dir', 'sea_dir_s', 'sea_dir_i']:
        if col in test_df.columns:
            test_df[col] = test_df[col].astype('category').cat.codes

    # 스케일러 로드
    scaler_path = f'./changwoo/model/{region}/{region}_scaler.pkl'

    try:
        scaler = joblib.load(scaler_path)
    except Exception as e:
        print(f"[{region}] 스케일러 로드 실패: {e}")
        continue

    scaler_features = list(scaler.feature_names_in_)
    test_cols = list(test_df.columns)

    # 스케일러에 있지만 데이터에 없는 컬럼은 0으로 채움
    for col in scaler_features:
        if col not in test_cols:
            test_df[col] = 0

    # 데이터에 있지만 스케일러에 없는 컬럼은 제거
    common_features = [c for c in scaler_features if c in test_df.columns]

    # 스케일링용 데이터 준비 (순서 맞춰서)
    X_test = test_df[scaler_features].fillna(0)

    try:
        X_test_scaled = scaler.transform(X_test)
    except Exception as e:
        print(f"[{region}] 스케일링 중 오류 발생: {e}")
        continue

    pred_result = pd.DataFrame()

    for col in scaler_features:
        try:
            model_path = f'./changwoo/model/{region}/{col}_model.h5'
            model = load_model(model_path)
        except Exception as e:
            print(f"[{region}/{col}] 모델 로드 실패: {e}")
            continue

        try:
            y_pred = np.argmax(model.predict(X_test_scaled, verbose=0), axis=1)
            pred_result[f"{col}_pred"] = y_pred

            y_true = test_df[col].values if col in test_df.columns else None
            if y_true is None:
                print(f"[{region}/{col}] 실제값이 없어 성능 평가 생략")
                continue

            if not np.issubdtype(y_true.dtype, np.integer):
                bins = np.linspace(np.min(y_true), np.max(y_true), bins_num + 1)
                y_true = np.digitize(y_true, bins) - 1

            save_summary_log(region, col, y_true, y_pred)

        except Exception as e:
            print(f"[{region}/{col}] 예측/평가 중 오류 발생: {e}")

    out_path = f"{predict_dir}/{region}_202406_pred.csv"
    pred_result.to_csv(out_path, index=False)
    print(f"저장: {out_path}")

print("\n=== 모든 2024-06 예측값 저장 완료 ===")
