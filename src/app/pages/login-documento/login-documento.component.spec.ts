import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LoginDocumentoComponent } from './login-documento.component';

describe('LoginDocumentoComponent', () => {
  let component: LoginDocumentoComponent;
  let fixture: ComponentFixture<LoginDocumentoComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LoginDocumentoComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(LoginDocumentoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
