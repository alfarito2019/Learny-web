import { Component, OnInit }   from '@angular/core';
import { CommonModule }         from '@angular/common';
import { Router, ActivatedRoute } from '@angular/router';
import { UsuarioService, UsuarioResponse } from '../../services/usuario.service';
import { HttpClientModule }     from '@angular/common/http';
@Component({
  selector: 'app-dashboard',
  imports: [CommonModule, HttpClientModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
})
export class DashboardComponent {
  cedula: string = '';
  nombre: string = '';
  error:  string = ''; 

  constructor(
    private route:    ActivatedRoute,
    private usuarioSvc: UsuarioService,
    private router:   Router) {}

  ngOnInit() {
    // Aquí lees la cédula que vino como ?cedula=1234

    this.route.queryParams.subscribe(params => {
      this.cedula = params['cedula'] || '';
      console.log('Cédula recibida:', this.cedula);
    });

    if (this.cedula) {
      this.cargarNombre();
    }
  }

  cargarNombre() {
    this.usuarioSvc.obtenerUsuario(this.cedula).subscribe({
      next: (res: UsuarioResponse) => {
        if (res.status === 'ok' && res.nombre) {
          this.nombre = res.nombre;
        } else {
          this.error = res.detail || 'Usuario no encontrado';
        }
      },
      error: err => {
        this.error = err.error?.detail || 'Error al conectar con el servidor';
      }
    });
  }

  mostrarAsistente() {
    this.router.navigate(['/chat'], { queryParams: { cedula: this.cedula} });
  }
}
