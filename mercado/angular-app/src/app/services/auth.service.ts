import { Injectable, PLATFORM_ID, Inject } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

const BASE_URL = 'http://localhost:8000';

@Injectable({ providedIn: 'root' })
export class AuthService {

  constructor(
    private http: HttpClient,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  private isBrowser(): boolean {
    return isPlatformBrowser(this.platformId);
  }

  // ── sessionStorage para cliente (por pestaña, no se comparte) ─────────────
  private setSession(key: string, value: string): void {
    if (this.isBrowser()) sessionStorage.setItem(key, value);
  }

  private getSession(key: string): string | null {
    return this.isBrowser() ? sessionStorage.getItem(key) : null;
  }

  private removeSession(key: string): void {
    if (this.isBrowser()) sessionStorage.removeItem(key);
  }

  // ── localStorage solo para restaurante (una sola sesión de restaurante) ────
  private setLocal(key: string, value: string): void {
    if (this.isBrowser()) localStorage.setItem(key, value);
  }

  private getLocal(key: string): string | null {
    return this.isBrowser() ? localStorage.getItem(key) : null;
  }

  private removeLocal(key: string): void {
    if (this.isBrowser()) localStorage.removeItem(key);
  }

  // ── Login cliente ─────────────────────────────────────────────────────────
  loginInvitado(telefono: string): Observable<any> {
    return this.http.post(`${BASE_URL}/usuarios/login-invitado`, { telefono }).pipe(
      tap((response: any) => {
        if (response?.access_token) {
          // Limpiar sesión de cliente anterior en esta pestaña
          sessionStorage.clear();
          this.setSession('token', response.access_token);
          this.setSession('rol', response.rol);
          this.setSession('telefono_cliente', telefono);
        }
      })
    );
  }

  // ── Login restaurante ─────────────────────────────────────────────────────
  loginRestaurante(id_comercial: string, contrasena: string): Observable<any> {
    return this.http.post(`${BASE_URL}/restaurantes/login`, { id_comercial, contrasena }).pipe(
      tap((response: any) => {
        if (response?.access_token) {
          this.removeLocal('restaurante_token');
          this.removeLocal('restaurante_id');
          this.removeLocal('restaurante_id_comercial');
          this.removeLocal('restaurante_nombre');
          this.setLocal('restaurante_token', response.access_token);
          this.setLocal('restaurante_id', String(response.id_restaurante));
          this.setLocal('restaurante_id_comercial', response.id_comercial);
          this.setLocal('restaurante_nombre', response.nombre);
        }
      })
    );
  }

  getRestaurantes(): Observable<any> {
    return this.http.get(`${BASE_URL}/restaurantes`);
  }

  // ── Getters cliente (sessionStorage) ─────────────────────────────────────
  getToken(): string | null { return this.getSession('token'); }
  getRol(): string | null { return this.getSession('rol'); }
  getTelefono(): string | null { return this.getSession('telefono_cliente'); }

  // ── Getters restaurante (localStorage) ───────────────────────────────────
  getRestauranteToken(): string | null { return this.getLocal('restaurante_token'); }
  getRestauranteNombre(): string | null { return this.getLocal('restaurante_nombre'); }
  getRestauranteIdComercial(): string | null { return this.getLocal('restaurante_id_comercial'); }

  isLoggedIn(): boolean { return !!this.getToken(); }
  isRestauranteLoggedIn(): boolean { return !!this.getRestauranteToken(); }
  isCliente(): boolean { return this.getRol() === 'cliente'; }

  logout(): void {
    sessionStorage.clear();
    this.removeLocal('restaurante_token');
    this.removeLocal('restaurante_id');
    this.removeLocal('restaurante_id_comercial');
    this.removeLocal('restaurante_nombre');
  }
}
