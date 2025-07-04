import pickle
import shap

def load_model():
    with open("app/ml_models/student_performance_model.pkl", "rb") as f:
        return pickle.load(f)

model = load_model()

xgb_model = model.named_steps['model']      # The XGBoost model
imputer = model.named_steps['imputer']      # The Imputer used in pipeline

#-------Initialize SHAP Explainer-------
explainer = shap.TreeExplainer(xgb_model)

def load_exam_avg_model():
    with open("app/ml_models/avg_exam_model.pkl", "rb") as f:
        return pickle.load(f)
    
avg_model = load_exam_avg_model()