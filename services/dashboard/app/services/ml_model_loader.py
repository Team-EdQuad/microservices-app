import pickle

def load_model():
    with open("app/ml_models/student_performance_model.pkl", "rb") as f:
        return pickle.load(f)

model = load_model()
