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

# 예측값 저장 폴더
predict_dir = './changwoo/predict'
os.makedirs(predict_dir, exist_ok=True)

# 요약 저장 경로
summary_path = './changwoo/predict/results_summary.txt'

def save_summary_log(region, item, y_true, y_pred, save_path=summary_path):
    acc = accuracy_score(y_true, y_pred)
    report = classification_report(y_true, y_pred, digits=4, zero_division=0)
    log = f"\n--- [{region} / {item}] ---\n"
    log += f"분류 정확도 (accuracy): {acc:.4f}\n"
    log += f"{report}\n"

    with open(save_path, 'a', encoding='utf-8') as f:
        f.write(log)
    print(log)  # 콘솔 출력

for region in regions:
    print(f"\n=== {region} 2024-06 예측 시작 ===")
    test_path = f'./finalData/{region}_06.csv'
    try:
        test_df = pd.read_csv(test_path)
    except Exception as e:
        print(f"[{region}] 테스트 데이터 로드 실패: {e}")
        continue

    # 실제 파일에 존재하는 컬럼만 추출
    test_cols = set(test_df.columns)
    valid_cols = [col for col in input_cols if col in test_cols]

    # 방향 변수 라벨 인코딩
    for col in ['wind_dir', 'sea_dir_s', 'sea_dir_i']:
        if col in valid_cols:
            test_df[col] = test_df[col].astype('category').cat.codes

    # 스케일러 불러오기 (지역별)
    scaler_path = f'./changwoo/model/{region}/{region}_scaler.pkl'  # 수정: InCheon_scaler.pkl 형태 대응
    if not os.path.exists(scaler_path):
        print(f"[{region}] 스케일러 파일 없음: {scaler_path} 예측 스킵")
        continue

    try:
        scaler = joblib.load(scaler_path)
    except Exception as e:
        print(f"[{region}] 스케일러 로드 실패: {e} 예측 스킵")
        continue

    # 스케일러가 기대하는 컬럼 리스트 가져오기
    if hasattr(scaler, 'feature_names_in_'):
        expected_features = list(scaler.feature_names_in_)
    else:
        expected_features = valid_cols

    # 테스트 데이터에 expected_features가 없으면 0으로 채워 넣음
    X_test_selected = test_df.reindex(columns=expected_features, fill_value=0).fillna(0)

    try:
        X_test_scaled = scaler.transform(X_test_selected)
    except Exception as e:
        print(f"[{region}] 스케일링 중 오류 발생: {e} 예측 스킵")
        continue

    pred_result = pd.DataFrame()
    for col in valid_cols:
        model_path = f'./changwoo/model/{region}/{col}_model.h5'
        if not os.path.exists(model_path):
            print(f"[{region}/{col}] 모델 파일 없음: {model_path} 예측 스킵")
            continue

        try:
            model = load_model(model_path)
            y_pred = np.argmax(model.predict(X_test_scaled, verbose=0), axis=1)
            pred_result[f"{col}_pred"] = y_pred

            # 실제값 (라벨) 가져오기
            y_true = test_df[col].values

            # y_true가 범주형 정수인지 확인
            if not np.issubdtype(y_true.dtype, np.integer):
                bins = np.linspace(np.min(y_true), np.max(y_true), bins_num + 1)
                y_true = np.digitize(y_true, bins) - 1

            save_summary_log(region, col, y_true, y_pred)

        except Exception as e:
            print(f"[{region}/{col}] 예측 중 오류 발생: {e}")

    out_path = f"{predict_dir}/{region}_202406_pred.csv"
    pred_result.to_csv(out_path, index=False)
    print(f"저장: {out_path}")

print("\n=== 모든 2024-06 예측값 저장 완료 ===")
