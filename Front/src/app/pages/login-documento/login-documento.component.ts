import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login-documento',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login-documento.component.html',
  styleUrls: ['./login-documento.component.scss']
})
export class LoginDocumentoComponent {
  tipoDocumentoOptions = [
    'Cédula de ciudadanía',
    'Tarjeta de identidad',
    'Cédula de extranjería'
  ];
  selectedTipo: string = this.tipoDocumentoOptions[0];
  numeroDocumento: string = '';
  validDocumento: boolean = false;

  constructor(private router: Router) {}

  onTipoChange(value: string) {
    this.selectedTipo = value;
  }

  onNumeroChange(value: string) {
    this.numeroDocumento = value;
    // Simulación de verificación: solo números con al menos 6 dígitos
    this.validDocumento = /^[0-9]{6,}$/.test(value);
  }

  goBack() {
    this.router.navigate(['/welcome']);
  }

  goNext() {
    console.log(this.numeroDocumento);
    if (this.validDocumento) {
      this.router.navigate(['/login/clave'], {
        queryParams: { cedula: this.numeroDocumento }
        
      });
    }
  }
}
