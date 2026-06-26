from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import pandas as pd
import sqlite3
from datetime import datetime
import ollama 

app = FastAPI()

# Allow your Angular frontend to talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the trained AI Brain
with open("brain_v2.pkl", "rb") as f:
    model = pickle.load(f)

# --- DATABASE SETUP ---
def setup_database():
    conn = sqlite3.connect("clinical_records.db")
    cursor = conn.cursor()
    # Create a table if it doesn't exist yet
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patient_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            age INTEGER,
            bmi REAL,
            glucose INTEGER,
            diagnosis TEXT,
            confidence REAL
        )
    """)
    conn.commit()
    conn.close()

# Run the setup the moment the server turns on
setup_database()
# ---------------------------

# --- CORRECTED MODEL WITH DEFAULTS ---
class PatientData(BaseModel):
    Age: int
    Glucose: float
    BloodPressure: float
    BMI: float
    Insulin: float
    Pregnancies: int
    # Providing defaults here solves the 422 error if Angular sends empty fields!
    SkinThickness: float = 20.0 
    DiabetesPedigreeFunction: float = 0.5


# ==========================================
# 🚀 ROUTE 1: THE AI PREDICTION ENGINE
# ==========================================
@app.post("/api/predict")
def predict_diabetes(data: PatientData):
    # 1. Format the data for the AI
    input_dict = data.model_dump() 
    features_list = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
    input_data = pd.DataFrame([input_dict])
    input_data = input_data[features_list] 
    
    # 2. Make the prediction
    prediction = model.predict(input_data)[0]
    probabilities = model.predict_proba(input_data)[0]
    confidence = float(max(probabilities))
    result_label = "Diabetic" if prediction == 1 else "Non-Diabetic"

    # --- 3. SMART PERSONALIZED ADVICE ENGINE ---
    concerns = []
    
    # The AI checks the specific patient's actual numbers!
    if data.Glucose > 125:
        concerns.append("lowering your high blood sugar with a low-carb diet")
    elif data.Glucose < 70:
        concerns.append("monitoring your low blood sugar levels")
        
    if data.BMI > 25.0:
        concerns.append("maintaining a healthy weight through consistent exercise")
        
    if data.BloodPressure > 130:
        concerns.append("reducing sodium intake to manage blood pressure")

    # Generate a dynamic message based on what is actually wrong with them
    if len(concerns) >= 2:
        patient_message = f"Based on your specific vitals, we strongly recommend {concerns[0]}, and additionally {concerns[1]}."
    elif len(concerns) == 1:
        patient_message = f"Based on your vitals, your primary clinical focus should be {concerns[0]}."
    else:
        patient_message = "Your clinical vitals are currently within healthy ranges. Keep up the good work and maintain a balanced lifestyle! 🥗"
    # ----------------------------------------

    # Keep your top_factors the same for the UI progress bars
    importances = model.feature_importances_
    symptom_scores = sorted(zip(features_list, importances), key=lambda x: x[1], reverse=True)
    top_factors = [{"name": name, "impact": round(float(score) * 100, 1)} for name, score in symptom_scores[:2]]
        
    ai_explanation = f"Global model drivers: {top_factors[0]['name']} ({top_factors[0]['impact']}%) and {top_factors[1]['name']} ({top_factors[1]['impact']}%)."

    # --- 4. SAVE TO DATABASE ---
    conn = sqlite3.connect("clinical_records.db")
    cursor = conn.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO patient_history (timestamp, age, bmi, glucose, diagnosis, confidence)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (current_time, data.Age, data.BMI, data.Glucose, result_label, confidence))
    
    conn.commit()
    conn.close()

    # 5. Send everything back to Angular
    return {
        "prediction": int(prediction),
        "label": result_label,
        "confidence_score": confidence,
        "top_risk_factors": top_factors, 
        "explanation": ai_explanation,
        "patient_message": patient_message # Now it changes based on user input!
    }

# ==========================================
# 📋 ROUTE 2: THE CLINICAL HISTORY DATABASE
# ==========================================
@app.get("/api/history")
def get_patient_history():
    conn = sqlite3.connect("clinical_records.db")
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM patient_history ORDER BY timestamp DESC LIMIT 50")
    records = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in records]

# ==========================================
# 🤖 ROUTE 3: THE VIRTUAL CLINICAL CONSULTANT
# ==========================================
@app.post("/api/chat")
def chat_with_ai(data: dict):
    user_question = data.get("question")
    context = data.get("context") 
    
    # This prompt contains your formatting and medical persona instructions!
    prompt = f"""
    You are a friendly, highly engaging Virtual Medical Assistant speaking to a patient. 
    Context (Vitals & Diagnosis): {context}
    Patient Question: {user_question}
    
    CRITICAL INSTRUCTIONS:
    1. Tone: Warm, encouraging, and highly readable.
    2. Format: Break your answer into VERY short paragraphs (1-2 sentences maximum). 
    3. Structure: Use bullet points if you are listing multiple items or steps.
    4. Emojis: You MUST use relevant emojis naturally throughout your response! 🥗🏃‍♂️💪
    5. Disclaimer: End with a short, polite disclaimer that this is not a substitute for professional medical advice.
    """
    
    try:
        # We now pass the 'prompt' variable so the AI sees all your rules!
        response = ollama.chat(model='phi3', messages=[{'role': 'user', 'content': prompt}])
        return {"response": response['message']['content']}
        
    except Exception as e:
        print(f"AI Brain Error: {str(e)}")
        return {"response": "I am currently undergoing maintenance. Please consult your physician directly for immediate assistance. 🩺"}
    
# ==========================================
# 🔬 ROUTE 4: ADMIN RESEARCH (Uses Llama 3 for Logic)
# ==========================================
@app.post("/api/admin/research")
def research_admin(data: dict):
    topic = data.get("topic")
    
    # This prompt is designed for a professional medical researcher.
    # It focuses on academic depth but keeps the formatting clean!
    prompt = f"""
    You are a professional Medical Research Assistant. 
    Task: Provide a deep, academic, and structured analysis of the following topic: {topic}.
    
    INSTRUCTIONS:
    1. Tone: Professional, authoritative, and academic.
    2. Format: Use clear, concise paragraphs (2-3 sentences max).
    3. Structure: Use bullet points for key findings or clinical indicators.
    4. Readability: Bold the most critical clinical terms or data points.
    5. Disclaimer: End with a short note stating that this analysis is for research purposes only.
    """
    
    try:
        # We are using Llama 3 here for its superior reasoning capabilities!
        response = ollama.chat(model='llama3:8b-instruct-q4_0', messages=[{'role': 'user', 'content': prompt}])
        return {"response": response['message']['content']}
        
    except Exception as e:
        print(f"Admin Brain Error: {str(e)}")
        return {"response": "I'm currently unable to access the research database. Please check your system logs. 🔍"}