import pandas as pd
import mysql.connector
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle  # <-- 1. Changed to pickle to match your main.py server perfectly!

print("🧠 Connecting to database to fetch training data...")

# 1. Fetch data from your MySQL Database
try:
    connection = mysql.connector.connect(
        host='localhost',
        database='MedPredictDB',
        user='root',
        password='1234' # <-- Change to your MySQL password
    )
    
    # Query combining demographics and lab results
    query = """
        SELECT p.Pregnancies, l.Glucose, l.BloodPressure, 
               l.SkinThickness, l.Insulin, l.BMI, l.DiabetesPedigreeFunction, p.Age
        FROM Patients p
        JOIN LabResults l ON p.PatientID = l.PatientID
    """
    
    # Read directly into a clean Pandas DataFrame
    df = pd.read_sql(query, connection)
    connection.close()
    print(f"📊 Successfully pulled {len(df)} records for training.")

except mysql.connector.Error as err:
    print(f"❌ Database error: {err}")
    exit()

# 2. Separate Features (X) and Target Label (y)
csv_data = pd.read_csv('diabetes.csv')
y = csv_data['Outcome']
X = df # Our features from the database

# Split into 80% Training and 20% Testing data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("🤖 Training the Random Forest Classifier...")

# 3. Initialize and train the Machine Learning Model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Check how accurate our model is
accuracy = model.score(X_test, y_test)
print(f"🎯 Model Training Complete! Accuracy: {accuracy * 100:.2f}%")

# 4. Save the trained model brain to a NEW file to bypass Windows lock
with open('brain_v2.pkl', 'wb') as f:
    pickle.dump(model, f)  # <-- 2. Using pickle to save it!

print("💾 Model saved successfully as 'brain_v2.pkl'!")