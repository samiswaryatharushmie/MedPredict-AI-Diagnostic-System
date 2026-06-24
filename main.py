from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
import joblib
import numpy as np

app = FastAPI(title="MedPredict AI API")

# Enable CORS so your future Angular frontend can talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧠 Load the trained Machine Learning Model Brain
try:
    model = joblib.load('diabetes_model.pkl')
    print("🧠 Machine Learning Model loaded successfully!")
except Exception as e:
    print(f"⚠️ Could not load ML model file: {e}")

# Define the structure of data the API expects for a prediction
class PredictionInput(BaseModel):
    Pregnancies: int
    Glucose: float
    BloodPressure: float
    SkinThickness: float
    Insulin: float
    BMI: float
    DiabetesPedigreeFunction: float
    Age: int

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        database='MedPredictDB',
        user='root',
        password='YOUR_PASSWORD'  # <-- DO NOT FORGET TO CHANGE THIS TO YOUR PASSWORD!
    )

@app.get("/")
def home():
    return {"status": "success", "message": "Welcome to the MedPredict Medical API bridge!"}

@app.get("/api/patients/count")
def get_patient_count():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Patients")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return {"total_patients": count}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

@app.get("/api/patients")
def get_patients(limit: int = 10):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True) 
        query = """
            SELECT p.PatientID, p.Age, p.Pregnancies, 
                   l.Glucose, l.BloodPressure, l.BMI, l.Insulin
            FROM Patients p
            JOIN LabResults l ON p.PatientID = l.PatientID
            LIMIT %s
        """
        cursor.execute(query, (limit,))
        patients = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"status": "success", "data": patients}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

# 🚀 NEW ENDPOINT: Live AI Prediction
@app.post("/api/predict")
def predict_diabetes(input_data: PredictionInput):
    if model is None:
        raise HTTPException(status_code=500, detail="ML model is not loaded on the server.")
    
    try:
        features = np.array([[
            input_data.Pregnancies, input_data.Glucose, input_data.BloodPressure,
            input_data.SkinThickness, input_data.Insulin, input_data.BMI,
            input_data.DiabetesPedigreeFunction, input_data.Age
        ]])
        
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        confidence = float(probabilities[prediction])
        
        return {
            "status": "success",
            "prediction": int(prediction),
            "label": "Diabetic" if prediction == 1 else "Non-Diabetic",
            "confidence_score": round(confidence, 4)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")