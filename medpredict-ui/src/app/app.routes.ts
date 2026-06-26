import { Routes } from '@angular/router';
import { PatientViewComponent } from './patient-view/patient-view';
import { AdminViewComponent } from './admin-view/admin-view';

export const routes: Routes = [
  { path: '', redirectTo: '/patient', pathMatch: 'full' },
  { path: 'patient', component: PatientViewComponent },
  { path: 'admin', component: AdminViewComponent }
];