import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoginService }    from '../../services/login.service';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute,Router } from '@angular/router';
@Component({
  selector: 'app-login-clave',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './login-clave.component.html',
  styleUrl: './login-clave.component.scss'
})
export class LoginClaveComponent {
  cedula: string = '';
  clave: string = '';
  error:  string = '';      // ← aquí declaras la variable error
  validDocumento: boolean = false;
  constructor(
    private route:    ActivatedRoute,
    private loginSvc: LoginService,
    private router: Router) {}


    ngOnInit() {
    // Aquí lees la cédula que vino como ?cedula=1234
    this.route.queryParams.subscribe(params => {
      this.cedula = params['cedula'] || '';
      console.log('Cédula recibida:', this.cedula);
    });
  }


  onClaveChange(value: string) {
  this.clave = value;
  // Si también quieres habilitar el botón usando validDocumento,
  // pon aquí la lógica de validación de la clave:
  this.validDocumento = value.length >= 4; 
}

  goBack() {
    this.router.navigate(['/login/documento']);
  }




  onSubmit() {
    this.error = '';  // limpia el mensaje de error previo
    this.loginSvc.login(this.cedula, this.clave).subscribe({
      next: resp => {
        if (resp.status === 'ok') {
          // Login correcto: navegar a /chat u otra ruta
          this.router.navigate(['/chat'], { queryParams: { nombre: resp.nombre } });
        } else {
          // Status error con detail
          this.error = resp.detail || 'Error desconocido';
        }
      },
      error: err => {
        // Error HTTP (por ejemplo 401)
        this.error = err.error?.detail || 'Credenciales incorrectas';
      }
    });
  }

}
