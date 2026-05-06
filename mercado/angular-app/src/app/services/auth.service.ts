import { Injectable, PLATFORM_ID, Inject } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

const BASE_URL = 'http://localhost:8000';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  constructor(
    private http: HttpClient,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  // ── Login cliente: solo teléfono ──────────────────────────────────────────
  loginInvitado(telefono: string): Observable<any> {
    return this.http.post(`${BASE_URL}/usuarios/login-invitado`, { telefono }).pipe(
      tap((response: any) => {
        if (response?.access_token) {
          this.setUserSession(response.access_token, response.rol);
        }
      })
    );
  }

  // ── Login restaurante: id_comercial + contraseña ──────────────────────────
  loginRestaurante(id_comercial: string, contrasena: string): Observable<any> {
    return this.http.post(`${BASE_URL}/restaurantes/login`, { id_comercial, contrasena }).pipe(
      tap((response: any) => {
        if (response?.access_token) {
          this.setRestauranteSession(
            response.access_token,
            response.id_restaurante,
            response.id_comercial,
            response.nombre,
          );
        }
      })
    );
  }

  getRestaurantes(): Observable<any> {
    return this.http.get(`${BASE_URL}/restaurantes`);
  }

  // ── Sesión usuario ────────────────────────────────────────────────────────
  private setUserSession(token: string, rol: string): void {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.setItem('token', token);
      localStorage.setItem('rol', rol);
      localStorage.removeItem('restaurante_token');
      localStorage.removeItem('restaurante_id');
      localStorage.removeItem('restaurante_nombre');
    }
  }

  // ── Sesión restaurante ────────────────────────────────────────────────────
  private setRestauranteSession(token: string, id: number, idComercial: string, nombre: string): void {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.setItem('restaurante_token', token);
      localStorage.setItem('restaurante_id', String(id));
      localStorage.setItem('restaurante_id_comercial', idComercial);
      localStorage.setItem('restaurante_nombre', nombre);
      localStorage.removeItem('token');
      localStorage.removeItem('rol');
    }
  }

  getToken(): string | null {
    if (isPlatformBrowser(this.platformId)) return localStorage.getItem('token');
    return null;
  }

  getRestauranteToken(): string | null {
    if (isPlatformBrowser(this.platformId)) return localStorage.getItem('restaurante_token');
    return null;
  }

  getRol(): string | null {
    if (isPlatformBrowser(this.platformId)) return localStorage.getItem('rol');
    return null;
  }

  getRestauranteNombre(): string | null {
    if (isPlatformBrowser(this.platformId)) return localStorage.getItem('restaurante_nombre');
    return null;
  }

  getRestauranteIdComercial(): string | null {
    if (isPlatformBrowser(this.platformId)) return localStorage.getItem('restaurante_id_comercial');
    return null;
  }

  isLoggedIn(): boolean { return !!this.getToken(); }
  isRestauranteLoggedIn(): boolean { return !!this.getRestauranteToken(); }
  isCliente(): boolean { return this.getRol() === 'cliente'; }

  logout(): void {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem('token');
      localStorage.removeItem('rol');
      localStorage.removeItem('restaurante_token');
      localStorage.removeItem('restaurante_id');
      localStorage.removeItem('restaurante_id_comercial');
      localStorage.removeItem('restaurante_nombre');
    }
  }
}
