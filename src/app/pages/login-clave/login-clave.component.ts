import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
@Component({
  selector: 'app-login-clave',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './login-clave.component.html',
  styleUrl: './login-clave.component.scss'
})
export class LoginClaveComponent {
  numeroDocumento: string = '';
  validDocumento: boolean = false;

  constructor(private router: Router) {}


  onNumeroChange(value: string) {
    this.numeroDocumento = value;
    // Simulación de verificación: solo números con al menos 4 dígitos
    this.validDocumento = /^[0-9]{4,}$/.test(value);
  }

  goBack() {
    this.router.navigate(['/login/documento']);
  }

  goNext() {
    if (this.validDocumento) {
      this.router.navigate(['/chat'], {
        queryParams: { cedula: this.numeroDocumento }
      });
    }
  }
}
