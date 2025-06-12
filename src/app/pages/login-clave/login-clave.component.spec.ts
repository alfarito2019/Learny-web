import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LoginClaveComponent } from './login-clave.component';

describe('LoginClaveComponent', () => {
  let component: LoginClaveComponent;
  let fixture: ComponentFixture<LoginClaveComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LoginClaveComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(LoginClaveComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
