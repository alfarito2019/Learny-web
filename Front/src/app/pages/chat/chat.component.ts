import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { ActivatedRoute, Router } from '@angular/router';

interface Message {
  text: string;
  sender: 'user' | 'bot';
  time: string;
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss'],
})
export class ChatComponent {
  cedula: string = '';
  loading = false;
  constructor(private http: HttpClient, private router: Router,private route:    ActivatedRoute,) {}
  mostrarBotones: boolean = false;
  messages: Message[] = [
    {
      text: 'Buenos días señor Daniel. Bienvenido a Davivienda ¿en qué puedo ayudarle?',
      sender: 'bot',
      time: this.getCurrentTime(),
    },
  ];

  inputMessage: string = '';

ngOnInit() {
    // Aquí lees la cédula que vino como ?cedula=1234
    this.route.queryParams.subscribe(params => {
      this.cedula = params['cedula'] || '';
      console.log('Cédula recibida:', this.cedula);
    });
  }

  sendMessage() {
    const messageText = this.inputMessage.trim();
    if (!messageText) return;

    const time = this.getCurrentTime();

    // Mensaje del usuario
    this.messages.push({
      text: messageText,
      sender: 'user',
      time,
    });

    this.inputMessage = '';

    // Llamada a la API Flask en localhost:5000/chat
    this.http
      .post<any>('http://localhost:5000/chat', { mensaje: messageText })
      .subscribe({
        next: (response) => {
          this.messages.push({
            text: response.respuesta,
            sender: 'bot',
            time,
          });

          this.mostrarBotones = response.mostrar_botones; // 👈 activa los botones
        },
        error: () => {
          this.messages.push({
            text: 'Lo siento, ocurrió un error al contactar con el servidor.',
            sender: 'bot',
            time,
          });
        },
      });
  }

  generarInfografia(cedulas: string) {

    

    console.log('Generando infografía...');

    const cedula = this.cedula; // Reemplaza con la cédula real del usuario

    this.loading = true;

    this.http
      .post<any>('http://localhost:5001/generar-imagen', { cedula })
      .subscribe({
        next: (response) => {
          this.loading = false;
          const imageUrl = response.imagen_url;
          this.router.navigate(['/mostrar-imagen'], {
            state: { imagePath: imageUrl },
          });
        },
        error: (error) => {
          this.loading = false;
          console.error('Error al generar imagen:', error);
        },
      });
  }

  generarVideo() {
    console.log('Generando video...');
  }

  getCurrentTime(): string {
    return new Date().toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    });
  }
}
