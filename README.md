# 🩺 MedPredict AI: Clinical Diagnostic System

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.103.1-009688.svg)
![Angular](https://img.shields.io/badge/Angular-18.0+-DD0031.svg)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Scikit--Learn-F7931E.svg)

## 📌 Overview
MedPredict AI is an end-to-end, full-stack machine learning application designed for clinical environments. It takes real-time patient vitals and utilizes a trained Random Forest classification model to provide instant diagnostic predictions regarding diabetes risk.

This project demonstrates the complete lifecycle of an AI application: from raw data cleaning and model training to deploying a high-speed REST API and building a responsive, enterprise-grade clinical dashboard.

## 🚀 Features
* **Machine Learning Engine:** Trained on clinical datasets utilizing `scikit-learn` with data normalization and feature engineering.
* **High-Speed API:** Backend powered by `FastAPI` to serve the serialized ML model with millisecond latency.
* **Modern Clinical UI:** A responsive, glassmorphism-styled frontend built with modern `Angular` (Zoneless Change Detection).
* **Simulated Inference Delay:** Engineered UI/UX to provide realistic processing feedback for clinical users.

## 🛠️ Technology Stack
* **Data Science:** Pandas, NumPy, Scikit-Learn, Pickle
* **Backend Server:** Python, FastAPI, Uvicorn
* **Frontend Application:** Angular, TypeScript, HTML5, Modern CSS3

## ⚙️ How to Run Locally

### 1. Start the AI Server (Backend)
Navigate to the root directory and start the Uvicorn server:
```bash
uvicorn main:app --reload