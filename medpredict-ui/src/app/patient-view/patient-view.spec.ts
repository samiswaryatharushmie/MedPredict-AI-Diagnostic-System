import { ComponentFixture, TestBed } from '@angular/core/testing';

// 1. We added "Component" to the name here so it matches your main file
import { PatientViewComponent } from './patient-view';

describe('PatientViewComponent', () => {
  let component: PatientViewComponent;
  let fixture: ComponentFixture<PatientViewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PatientViewComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(PatientViewComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});