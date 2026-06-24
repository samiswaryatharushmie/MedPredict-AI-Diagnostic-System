import { Component, ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  patientData = {
    Age: null, Glucose: null, BloodPressure: null,
    BMI: null, Insulin: null, Pregnancies: null,
    SkinThickness: 20, DiabetesPedigreeFunction: 0.5 
  };

  predictionResult: any = null;
  errorMessage: string = '';
  isLoading: boolean = false; // <-- 1. New loading tracker!

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) {}

  runPrediction() {
    this.errorMessage = '';
    this.predictionResult = null;
    this.isLoading = true; // <-- 2. Turn on the loading animation!

    // 3. Add a dramatic 1.2-second delay so it feels like heavy AI processing
    setTimeout(() => {
      this.http.post('http://127.0.0.1:8000/api/predict', this.patientData)
        .subscribe({
          next: (result: any) => {
            this.predictionResult = result; 
            this.isLoading = false; // <-- Turn it off when done
            this.cdr.detectChanges();
          },
          error: (err) => {
            this.errorMessage = '⚠️ Could not connect to the AI Server.';
            this.isLoading = false; // <-- Turn it off on error
            this.cdr.detectChanges();
            console.error(err);
          }
        });
    }, 1200); 
  }
}