import os
import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import classification_report, accuracy_score
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.utils import to_categorical

regions = ['InCheon', 'Yeosu', 'Tongyeong', 'Taean', 'Uljin']
input_cols = ['sea_high', 'salt', 'wind_speed', 'wind_dir', 'temp', 'pressure',
              'sea_speed', 'sea_dir_s', 'sea_dir_i', 'sea_temp']
output_cols = input_cols.copy()
bins_num = 3

def to_categories(series, bins=bins_num):
    labels = range(bins)
    try:
        cat = pd.qcut(series, q=bins, labels=labels, duplicates='drop')
        if cat.isnull().any():
            cat = pd.cut(series, bins=bins, labels=labels, include_lowest=True)
    except Exception:
        cat = pd.cut(series, bins=bins, labels=labels, include_lowest=True)
    return cat.astype(int)

def build_model(input_dim, output_dim):
    model = Sequential([
        Dense(256, activation='relu', input_shape=(input_dim,)),
        BatchNormalization(),
        Dropout(0.2),
        Dense(128, activation='relu'),
        BatchNormalization(),
        Dropout(0.2),
        Dense(output_dim, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

for region in regions:
    print(f"\n=== {region} 모델 학습 및 저장 시작 ===")
    train_path = f'./finalData/{region}_04.csv'
    test_path  = f'./finalData/{region}_05.csv'
    train_df = pd.read_csv(train_path)
    test_df  = pd.read_csv(test_path)

    # 실제 파일에 존재하는 컬럼만 추출
    train_cols = set(train_df.columns)
    test_cols  = set(test_df.columns)
    valid_cols = [col for col in input_cols if col in train_cols and col in test_cols]

    # 빠진 컬럼 경고
    missing_cols = [col for col in input_cols if col not in train_cols or col not in test_cols]
    if missing_cols:
        print(f"⚠️ {region}에 없는 컬럼(건너뜀): {missing_cols}")

    # 방향 변수 라벨 인코딩 (있을 때만)
    for col in ['wind_dir', 'sea_dir_s', 'sea_dir_i']:
        if col in valid_cols:
            combined = pd.concat([train_df[col], test_df[col]], axis=0)
            categories = combined.astype('category').cat.categories
            train_df[col] = train_df[col].astype(pd.api.types.CategoricalDtype(categories=categories)).cat.codes
            test_df[col]  = test_df[col].astype(pd.api.types.CategoricalDtype(categories=categories)).cat.codes

    X_train = train_df[valid_cols]
    X_test  = test_df[valid_cols]

    # y 데이터 준비 (없는 컬럼은 제외)
    region_output_cols = [col for col in output_cols if col in valid_cols]
    y_train_cat = pd.DataFrame()
    y_test_cat  = pd.DataFrame()
    for col in region_output_cols:
        y_train_cat[col] = to_categories(train_df[col], bins=bins_num)
        y_test_cat[col]  = to_categories(test_df[col],  bins=bins_num)

    y_train_oh = {}
    y_test_oh  = {}
    for col in region_output_cols:
        y_train_oh[col] = to_categorical(y_train_cat[col], num_classes=bins_num)
        y_test_oh[col]  = to_categorical(y_test_cat[col],  num_classes=bins_num)

    scaler = RobustScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled  = scaler.transform(X_test)

    save_dir = f'./changwoo/model/{region}'
    os.makedirs(save_dir, exist_ok=True)

    # RobustScaler 저장!
    scaler_path = os.path.join(save_dir, f"{region}_scaler.pkl")
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)
    print(f"저장 완료: {scaler_path}")

    # 없는 컬럼은 자동 건너뜀!
    for col in region_output_cols:
        print(f'\n--- [{region} / {col}] 모델 학습 ---')
        input_dim = X_train_scaled.shape[1]
        output_dim = y_train_oh[col].shape[1]

        class_weights = compute_class_weight(
            class_weight='balanced',
            classes=np.unique(y_train_cat[col]),
            y=y_train_cat[col]
        )
        class_weight_dict = dict(enumerate(class_weights))

        model = build_model(input_dim, output_dim)
        early_stop = EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)

        history = model.fit(
            X_train_scaled, y_train_oh[col],
            validation_data=(X_test_scaled, y_test_oh[col]),
            epochs=100,
            batch_size=64,
            class_weight=class_weight_dict,
            callbacks=[early_stop],
            verbose=2
        )

        y_pred_probs = model.predict(X_test_scaled)
        y_pred_labels = np.argmax(y_pred_probs, axis=1)
        y_true_labels = np.argmax(y_test_oh[col], axis=1)

        acc = accuracy_score(y_true_labels, y_pred_labels)
        print(f"[{region} / {col}] 분류 정확도: {acc:.4f}")
        print(classification_report(y_true_labels, y_pred_labels))

        model_path = os.path.join(save_dir, f"{col}_model.h5")
        model.save(model_path)
        print(f"저장 완료: {model_path}")

print("\n모든 지역별 모델 저장 완료!")
