"""
Module quản lý Machine Learning models cho dự đoán rủi ro tín dụng
"""

import os
import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    accuracy_score,
    recall_score,
    precision_score,
    roc_auc_score,
)
from xgboost import XGBClassifier
from typing import Tuple, Dict

# Các cột features cho model (X_1 đến X_14)
MODEL_COLS = [f"X_{i}" for i in range(1, 15)]


class CreditRiskModels:
    """Class quản lý các ML models cho dự đoán rủi ro tín dụng"""

    def __init__(self):
        self.model_logistic = None
        self.model_rf = None
        self.model_xgb = None
        self.model_stacking = None
        self.is_trained = False

    def train_models(self, data_path: str) -> Dict:
        """
        Train các mô hình ML từ dữ liệu.

        Args:
            data_path: Path đến file CSV chứa dữ liệu training

        Returns:
            Dict chứa metrics của các models
        """
        # Đọc dữ liệu
        df = pd.read_csv(data_path)

        # Kiểm tra cột default và các cột X_1..X_14
        if 'default' not in df.columns:
            raise ValueError("Dataset phải có cột 'default'")

        # Tạo các cột X_1..X_14 nếu chưa có
        for i in range(1, 15):
            col = f"X_{i}"
            if col not in df.columns:
                raise ValueError(f"Dataset thiếu cột {col}")

        # Chuẩn bị dữ liệu
        X = df[MODEL_COLS]
        y = df['default'].astype(int)

        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # 1. Logistic Regression
        self.model_logistic = LogisticRegression(
            random_state=42,
            max_iter=1000,
            class_weight="balanced",
            solver="lbfgs"
        )
        self.model_logistic.fit(X_train, y_train)

        # 2. Random Forest
        self.model_rf = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=10,
            class_weight="balanced"
        )
        self.model_rf.fit(X_train, y_train)

        # 3. XGBoost
        self.model_xgb = XGBClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=6,
            learning_rate=0.1,
            use_label_encoder=False,
            eval_metric='logloss'
        )
        self.model_xgb.fit(X_train, y_train)

        # 4. Stacking Classifier (meta-model)
        estimators = [
            ('logistic', self.model_logistic),
            ('random_forest', self.model_rf),
            ('xgb', self.model_xgb)
        ]

        self.model_stacking = StackingClassifier(
            estimators=estimators,
            final_estimator=LogisticRegression(random_state=42, max_iter=1000),
            cv=5,  # Cross-validation 5-fold
            stack_method='predict_proba',  # Dùng probability để stack
            n_jobs=-1  # Sử dụng tất cả CPU cores
        )
        self.model_stacking.fit(X_train, y_train)

        self.is_trained = True

        # Tính metrics cho từng model
        metrics = {}
        for model_name, model in [
            ('Logistic', self.model_logistic),
            ('RandomForest', self.model_rf),
            ('XGBoost', self.model_xgb),
            ('Stacking', self.model_stacking)
        ]:
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)[:, 1]

            metrics[model_name] = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred, zero_division=0),
                'recall': recall_score(y_test, y_pred, zero_division=0),
                'f1': f1_score(y_test, y_pred, zero_division=0),
                'auc': roc_auc_score(y_test, y_proba)
            }

        return metrics

    def predict(self, features: pd.DataFrame) -> Dict:
        """
        Dự đoán xác suất vỡ nợ (PD) cho một doanh nghiệp.

        Args:
            features: DataFrame chứa 14 chỉ số tài chính (X_1 đến X_14)

        Returns:
            Dict chứa kết quả dự đoán từ tất cả các models
        """
        if not self.is_trained:
            raise ValueError("Models chưa được train. Hãy gọi train_models() trước.")

        # Đảm bảo có đủ 14 cột X_1..X_14
        features_subset = features[MODEL_COLS]

        results = {}

        # Predict với từng model
        for model_name, model in [
            ('Logistic', self.model_logistic),
            ('RandomForest', self.model_rf),
            ('XGBoost', self.model_xgb),
            ('Stacking', self.model_stacking)
        ]:
            pred_proba = model.predict_proba(features_subset)[0]
            pred_label = model.predict(features_subset)[0]

            results[model_name] = {
                'pd': pred_proba[1],  # Probability of default
                'label': 'Default' if pred_label == 1 else 'Non-Default'
            }

        return results

    def save_models(self, models_dir: str):
        """Lưu các models đã train vào file"""
        if not self.is_trained:
            raise ValueError("Models chưa được train")

        os.makedirs(models_dir, exist_ok=True)

        with open(os.path.join(models_dir, 'model_logistic.pkl'), 'wb') as f:
            pickle.dump(self.model_logistic, f)

        with open(os.path.join(models_dir, 'model_rf.pkl'), 'wb') as f:
            pickle.dump(self.model_rf, f)

        with open(os.path.join(models_dir, 'model_xgb.pkl'), 'wb') as f:
            pickle.dump(self.model_xgb, f)

        with open(os.path.join(models_dir, 'model_stacking.pkl'), 'wb') as f:
            pickle.dump(self.model_stacking, f)

    def load_models(self, models_dir: str):
        """Load các models đã lưu từ file"""
        try:
            with open(os.path.join(models_dir, 'model_logistic.pkl'), 'rb') as f:
                self.model_logistic = pickle.load(f)

            with open(os.path.join(models_dir, 'model_rf.pkl'), 'rb') as f:
                self.model_rf = pickle.load(f)

            with open(os.path.join(models_dir, 'model_xgb.pkl'), 'rb') as f:
                self.model_xgb = pickle.load(f)

            with open(os.path.join(models_dir, 'model_stacking.pkl'), 'rb') as f:
                self.model_stacking = pickle.load(f)

            self.is_trained = True
            return True
        except Exception as e:
            print(f"Lỗi khi load models: {e}")
            return False


# Singleton instance
_models_instance = None


def get_models_instance() -> CreditRiskModels:
    """Get singleton instance of CreditRiskModels"""
    global _models_instance
    if _models_instance is None:
        _models_instance = CreditRiskModels()
    return _models_instance
