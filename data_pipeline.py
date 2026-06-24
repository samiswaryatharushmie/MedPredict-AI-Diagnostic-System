import pandas as pd
import mysql.connector

print("Starting the medical data pipeline...")

# 1. Load the CSV Data
try:
    data = pd.read_csv('diabetes.csv')
    print(f"Successfully loaded {len(data)} patient records from CSV.")
except FileNotFoundError:
    print("Error: Could not find diabetes.csv. Make sure it is in the same folder!")
    exit()

# 2. Connect to the MySQL Database
try:
    connection = mysql.connector.connect(
        host='localhost',
        database='MedPredictDB',
        user='root',
        password='1234' # <-- CHANGE THIS TO YOUR MYSQL PASSWORD
    )
    cursor = connection.cursor()
    print("Connected to MySQL Database!")

    # 3. Loop through the data and insert into tables
    for index, row in data.iterrows():
        
        # First: Insert the patient demographics
        patient_sql = "INSERT INTO Patients (Age, Pregnancies) VALUES (%s, %s)"
        cursor.execute(patient_sql, (row['Age'], row['Pregnancies']))
        
        # Get the new PatientID that MySQL just created
        new_patient_id = cursor.lastrowid 

        # Second: Insert the lab results linked to that patient
        lab_sql = """INSERT INTO LabResults 
                     (PatientID, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        lab_values = (new_patient_id, row['Glucose'], row['BloodPressure'], 
                      row['SkinThickness'], row['Insulin'], row['BMI'], row['DiabetesPedigreeFunction'])
        cursor.execute(lab_sql, lab_values)

    # Save the changes to the database
    connection.commit()
    print("Pipeline Complete! All data successfully uploaded to MySQL. 🚀")

except mysql.connector.Error as err:
    print(f"Database Error: {err}")

finally:
    # Always close the connection when done
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()