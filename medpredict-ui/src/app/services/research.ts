import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class ResearchService { // <--- This word "export" is the most important part!
  researchHistory: { topic: string, result: string }[] = [];

  constructor() { }
}