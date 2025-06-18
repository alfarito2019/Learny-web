import { Injectable } from '@angular/core';
import { HttpClient }   from '@angular/common/http';
import { Observable }   from 'rxjs';

export interface UsuarioResponse {
  status: 'ok' | 'error';
  nombre?: string;
  detail?: string;
}

@Injectable({ providedIn: 'root' })
export class UsuarioService {
  constructor(private http: HttpClient) {}

  obtenerUsuario(cedula: string): Observable<UsuarioResponse> {
    // Angular enviará la petición a /api/usuario/:cedula
    return this.http.get<UsuarioResponse>(`/api/usuario/${cedula}`);
  }
}
