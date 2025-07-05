import pickle
import shap


def load_model():
    with open("app/ml_models/student_performance_model.pkl", "rb") as f:
        return pickle.load(f)

model = load_model()

xgb_model = model.named_steps['model']   
print(type(xgb_model))

booster = xgb_model.get_booster()   
imputer = model.named_steps['imputer']     

#-------Initialize SHAP Explainer-------
explainer = shap.TreeExplainer(booster)

def load_exam_avg_model():
    with open("app/ml_models/avg_exam_model.pkl", "rb") as f:
        return pickle.load(f)
    
avg_model = load_exam_avg_model()