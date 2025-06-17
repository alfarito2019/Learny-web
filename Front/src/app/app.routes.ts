// src/app/app.routes.ts

import { Routes } from '@angular/router';

import { WelcomeComponent }      from './pages/welcome/welcome.component';
import { LoginDocumentoComponent }   from './pages/login-documento/login-documento.component';
import { LoginClaveComponent }       from './pages/login-clave/login-clave.component';
import { ChatComponent }             from './pages/chat/chat.component';
import { MostrarImagenComponent }    from './pages/mostrar-imagen/mostrar-imagen.component';

export const appRoutes: Routes = [
  { path: '',             redirectTo: 'welcome', pathMatch: 'full' },
  { path: 'welcome',      component: WelcomeComponent },
  { path: 'login/documento', component: LoginDocumentoComponent },
  { path: 'login/clave',  component: LoginClaveComponent },
  { path: 'chat',         component: ChatComponent },
  { path: 'mostrar-imagen', component: MostrarImagenComponent }
];
