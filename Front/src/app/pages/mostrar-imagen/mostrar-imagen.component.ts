import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-mostrar-imagen',
  imports: [CommonModule],
  templateUrl: './mostrar-imagen.component.html',
  styleUrls: ['./mostrar-imagen.component.scss']
})
export class MostrarImagenComponent {
  imagePath: string = '';

  constructor(private router: Router) {
    const navigation = this.router.getCurrentNavigation();
    if (navigation?.extras?.state && navigation.extras.state['imagePath']) {
      this.imagePath = navigation.extras.state['imagePath'];
    } else {
      console.warn('No se recibió la imagen.');
    }
  }
}