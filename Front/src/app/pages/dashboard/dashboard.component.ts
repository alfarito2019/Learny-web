import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { LoginService } from '../../services/login.service';

@Component({
  selector: 'app-dashboard',
  imports: [],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
})
export class DashboardComponent {
  cedula: string = '';
  clave: string = ''; 

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

  mostrarAsistente() {
    this.router.navigate(['/chat'], { queryParams: { cedula: this.cedula} });
  }
}
