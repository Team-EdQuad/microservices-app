# import joblib
# import numpy as np

# class TimeAgent:
#     def __init__(self, model_path="models/time_model.pkl"):
#         self.model_path = model_path
#         self.load_model()

#     def load_model(self):
#         self.model = joblib.load(self.model_path)

#     def detect(self, hour: int) -> bool:
#         data = np.array([[hour]])
#         result = self.model.predict(data)
#         return result[0] == -1  # True if anomaly

#     def reload(self):
#         self.load_model()

import joblib
import numpy as np
from pathlib import Path

class TimeAgent:
    def __init__(self):
        # Get absolute path to app/anomaly_detection/models/time_model.pkl
        self.model_path = Path(__file__).resolve().parent.parent / "models" / "time_model.pkl"
        self.load_model()

    def load_model(self):
        self.model = joblib.load(self.model_path)

    def detect(self, hour: int) -> bool:
        data = np.array([[hour]])
        result = self.model.predict(data)
        return result[0] == -1  # True if anomaly

    def reload(self):
        self.load_model()
