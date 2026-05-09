import { Injectable, signal, PLATFORM_ID, Inject } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { AuthService } from '../services/auth.service';

const BASE_URL = 'http://localhost:8000';
const STORAGE_KEY = 'notificaciones_cliente';

export interface Notificacion {
  id: string;
  id_restaurante: number;
  numero_orden: string;
  restaurante: string;
  mensaje: string;
  fecha: string;
  leida: boolean;
}

@Injectable({ providedIn: 'root' })
export class NotificacionesService {

  private _notificaciones = signal<Notificacion[]>([]);
  private _pollingInterval: any = null;
  private _pedidosYaNotificados = new Set<string>();

  readonly notificaciones = this._notificaciones.asReadonly();
  readonly noLeidas = () => this._notificaciones().filter(n => !n.leida).length;

  constructor(
    private http: HttpClient,
    private authService: AuthService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
    if (isPlatformBrowser(this.platformId)) {
      this.cargarDesdeStorage();
    }
  }

  private cargarDesdeStorage() {
    try {
      const raw = sessionStorage.getItem(STORAGE_KEY);
      if (raw) {
        const data: Notificacion[] = JSON.parse(raw);
        this._notificaciones.set(data);
        data.forEach(n => this._pedidosYaNotificados.add(n.id));
      }
    } catch {}
  }

  private guardarEnStorage() {
    if (!isPlatformBrowser(this.platformId)) return;
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(this._notificaciones()));
  }

  iniciarPolling() {
    if (this._pollingInterval) return;
    this.verificarPedidosListos();
    this._pollingInterval = setInterval(() => this.verificarPedidosListos(), 8000);
  }

  detenerPolling() {
    if (this._pollingInterval) {
      clearInterval(this._pollingInterval);
      this._pollingInterval = null;
    }
  }

  private verificarPedidosListos() {
    const token = this.authService.getToken();
    if (!token) return;

    const headers = new HttpHeaders({ 'Authorization': `Bearer ${token}` });
    this.http.get<any[]>(`${BASE_URL}/mis-pedidos`, { headers }).subscribe({
      next: (pedidos) => {
        pedidos.filter(p => p.estado === 3).forEach(p => {
          const id = String(p.id_pedido);
          if (!this._pedidosYaNotificados.has(id)) {
            this._pedidosYaNotificados.add(id);
            const nueva: Notificacion = {
              id,
              id_restaurante: p.id_restaurante,
              numero_orden: p.numero_orden,
              restaurante: p.nombre_restaurante,
              mensaje: `Tu pedido ${p.numero_orden} en ${p.nombre_restaurante} está listo para recoger. 🔔`,
              fecha: new Date().toISOString(),
              leida: false,
            };
            this._notificaciones.update(ns => [nueva, ...ns]);
            this.guardarEnStorage();
          }
        });
      }
    });
  }

  marcarTodasLeidas() {
    this._notificaciones.update(ns => ns.map(n => ({ ...n, leida: true })));
    this.guardarEnStorage();
  }

  limpiar() {
    this._notificaciones.set([]);
    this._pedidosYaNotificados.clear();
    if (isPlatformBrowser(this.platformId)) sessionStorage.removeItem(STORAGE_KEY);
  }
}
