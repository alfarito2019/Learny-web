// src/app/services/login.service.ts
import { Injectable } from '@angular/core';
import { HttpClient }   from '@angular/common/http';
import { Observable }   from 'rxjs';

export interface LoginResponse {
  status: 'ok' | 'error';
  nombre?: string;
  detail?: string;
}

@Injectable({ providedIn: 'root' })
export class LoginService {
  constructor(private http: HttpClient) {}

  login(cedula: string, clave: string): Observable<LoginResponse> {
    // Angular enviará la petición a /api/login y el proxy la mandará a tu Flask
    return this.http.post<LoginResponse>('/api/login', { cedula, clave });
  }
}
