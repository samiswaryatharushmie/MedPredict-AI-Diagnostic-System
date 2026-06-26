import { Component, ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms'; // <--- CORRECT PATH
import { CommonModule, DecimalPipe } from '@angular/common'; // <--- CORRECT PATH

@Component({
  selector: 'app-patient-view',
  standalone: true,
  imports: [FormsModule, CommonModule, DecimalPipe],
  templateUrl: './patient-view.html'
})
export class PatientViewComponent {
  patientData: any = { Age: null, Glucose: null, BloodPressure: null, BMI: null, Insulin: null, Pregnancies: null };
  predictionResult: any = null;
  errorMessage: string = '';
  isLoading: boolean = false;
  chatHistory: { role: string, text: string }[] = [];
  userQuery: string = '';
  isChatLoading: boolean = false;

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) {}

  formatMessage(text: string): string {
    return text ? text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') : '';
  }

runPrediction() {
    // --- 1. NEW VALIDATION CHECK (Only Age, Glucose, and BMI are mandatory) ---
    if (!this.patientData.Age || !this.patientData.Glucose || !this.patientData.BMI) {
      this.predictionResult = null;
      this.errorMessage = "⚠️ Please enter at least your Age, Glucose, and BMI for an accurate AI diagnosis.";
      this.cdr.detectChanges();
      return; // This completely stops the function from sending data to Python!
    }

    // --- 2. DATA SUBMISSION (With Smart Defaults) ---
    const payload = {
      Age: Number(this.patientData.Age),
      Glucose: Number(this.patientData.Glucose),
      BMI: Number(this.patientData.BMI),
      
      // If the user leaves these blank, use safe, healthy defaults!
      BloodPressure: Number(this.patientData.BloodPressure || 80), 
      Insulin: Number(this.patientData.Insulin || 0), 
      Pregnancies: Number(this.patientData.Pregnancies || 0),
      
      // Backend requires these, so we send average static values
      SkinThickness: 20, 
      DiabetesPedigreeFunction: 0.5 
    };

    console.log("Sending data to server:", payload);

    this.errorMessage = '';
    this.predictionResult = null;
    this.isLoading = true;

    this.http.post('http://127.0.0.1:8000/api/predict', payload).subscribe({
      next: (res: any) => { 
        this.predictionResult = res; 
        this.isLoading = false; 
        this.cdr.detectChanges(); // Ensure the UI updates
      },
      error: (err) => { 
        // Show the real error message from the server
        console.error("Server Error Detail:", err);
        this.errorMessage = `⚠️ Server Error: ${err.error?.detail || 'Check your inputs'}`;
        this.isLoading = false; 
        this.cdr.detectChanges();
      }
    });
  }
  askConsultant() {
    if (!this.userQuery.trim()) return;
    this.chatHistory.push({ role: 'user', text: this.userQuery });
    this.isChatLoading = true;
    this.http.post('http://127.0.0.1:8000/api/chat', { question: this.userQuery }).subscribe({
      next: (res: any) => { this.chatHistory.push({ role: 'bot', text: res.response }); this.isChatLoading = false; this.userQuery = ''; },
      error: () => { this.isChatLoading = false; }
    });
  }
}