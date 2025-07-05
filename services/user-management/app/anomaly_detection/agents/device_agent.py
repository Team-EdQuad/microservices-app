import joblib
import numpy as np
from pathlib import Path

class DeviceAgent:
    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent  # points to app/anomaly_detection
        self.model_path = base_dir / "models" / "device_model.pkl"
        self.encoder_path = base_dir / "models" / "device_encoder.pkl"
        self.load_model()

    def load_model(self):
        self.model = joblib.load(self.model_path)
        self.encoder = joblib.load(self.encoder_path)

    def detect(self, device: str) -> bool:
        try:
            encoded = self.encoder.transform([device]).reshape(-1, 1)
        except ValueError:
            return True  # unknown device = anomaly
        result = self.model.predict(encoded)
        return result[0] == -1

    def reload(self):
        self.load_model()
