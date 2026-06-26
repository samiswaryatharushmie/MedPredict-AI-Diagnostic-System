import { Component, ChangeDetectorRef, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ResearchService } from '../services/research'; 

@Component({
  selector: 'app-admin-view',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './admin-view.html'
})
export class AdminViewComponent implements OnInit {
  // --- DATABASE VARIABLES ---
  activeTab: 'database' | 'research' = 'database';
  clinicalHistory: any[] = [];
  isHistoryLoading: boolean = false;

  // --- LLAMA 3 RESEARCH VARIABLES ---
  researchTopic: string = '';
  isResearchLoading: boolean = false;
  
  // Note: We removed the local researchHistory array. 
  // We will now use 'this.researchService.researchHistory' instead!

  constructor(
    private http: HttpClient, 
    private cdr: ChangeDetectorRef,
    public researchService: ResearchService // <-- Service is injected here
  ) {}

  ngOnInit() {
    this.loadClinicalHistory();
  }

  async loadClinicalHistory() {
    this.isHistoryLoading = true;
    try {
      const response = await fetch('http://127.0.0.1:8000/api/history');
      this.clinicalHistory = await response.json();
    } catch (e) {
      console.error("Database connection failed:", e);
    }
    this.isHistoryLoading = false;
    this.cdr.detectChanges();
  }

  // --- 🔬 LLAMA 3 RESEARCH FUNCTION ---
  runResearch() {
    if (!this.researchTopic.trim()) return;

    const currentTopic = this.researchTopic; 
    this.researchTopic = ''; 

    this.isResearchLoading = true;
    this.cdr.detectChanges();

    this.http.post('http://127.0.0.1:8000/api/admin/research', { topic: currentTopic })
      .subscribe({
        next: (res: any) => {
          const formattedResult = res.response.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
          
          // Using the Service's history array so it persists across navigation
          this.researchService.researchHistory.unshift({
            topic: currentTopic,
            result: formattedResult
          });

          this.isResearchLoading = false;
          this.cdr.detectChanges();
        },
        error: (err) => {
          console.error("Research Error:", err);
          // Using the Service's history array
          this.researchService.researchHistory.unshift({
            topic: currentTopic,
            result: "⚠️ Connection error: Could not reach the Llama 3 Research server. Make sure Ollama is running!"
          });
          this.isResearchLoading = false;
          this.cdr.detectChanges();
        }
      });
  }
}