import joblib
import numpy as np

# โหลดโมเดลแค่ครั้งเดียว
model = joblib.load('model.pkl')

def predict_lgbm(features):
    """
    รับ features เป็น list แล้ว return ผลการพยากรณ์
    """
    input_data = np.array(features).reshape(1, -1)
    prediction = model.predict(input_data)
    return prediction.tolist()
