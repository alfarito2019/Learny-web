import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class AuthService {
  login(documento: string, clave: string): boolean {
    return documento === '123' && clave === 'abc'; // Prueba básica
  }
}