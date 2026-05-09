import { Component, OnInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { NotificacionesService } from './notificaciones.service';
import { AuthService } from '../services/auth.service';

const BASE_URL = 'http://localhost:8000';

@Component({
  selector: 'app-notificaciones',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './notificaciones.component.html',
  styleUrl: './notificaciones.component.css'
})
export class NotificacionesComponent implements OnInit, OnDestroy {

  abierto = false;
  calificacionesTemp: { [id: string]: number } = {};
  comentariosTemp: { [id: string]: string } = {};
  calificacionesEnviadas: { [id: string]: number } = {};

  constructor(
    public notifSvc: NotificacionesService,
    private authService: AuthService,
    private http: HttpClient,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
  if (this.authService.isLoggedIn()) {
    this.notifSvc.iniciarPolling();
  }
  try {
    const raw = sessionStorage.getItem('calificaciones_enviadas');
    if (raw) this.calificacionesEnviadas = JSON.parse(raw);
  } catch {}
  
  this.cargarCalificacionesPrevias();
}

  ngOnDestroy() { this.notifSvc.detenerPolling(); }

  abrir() { this.abierto = true; this.notifSvc.marcarTodasLeidas(); }
  cerrar() { this.abierto = false; }

  formatFecha(iso: string): string {
    const d = new Date(iso);
    return d.toLocaleDateString('es-CO', { day: '2-digit', month: 'short' }) +
           ' · ' + d.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
  }

  getCalificacionTemp(id: string): number {
    return this.calificacionesTemp[id] || 0;
  }

  setCalificacionTemp(id: string, valor: number) {
    this.calificacionesTemp[id] = valor;
    this.cdr.detectChanges();
  }

  // Verifica por restaurante — no por pedido
  calificacionDada(n: any): boolean {
    return Object.keys(this.calificacionesEnviadas).some(id => {
      const notif = this.notifSvc.notificaciones().find(x => x.id === id);
      return notif?.id_restaurante === n.id_restaurante;
    });
  }

  getCalificacionDada(n: any): number {
    const id = Object.keys(this.calificacionesEnviadas).find(id => {
      const notif = this.notifSvc.notificaciones().find(x => x.id === id);
      return notif?.id_restaurante === n.id_restaurante;
    });
    return id ? this.calificacionesEnviadas[id] : 0;
  }

  enviarCalificacion(notif: any) {
    const puntuacion = this.calificacionesTemp[notif.id];
    if (!puntuacion) return;

    const token = this.authService.getToken();
    if (!token) return;

    const headers = new HttpHeaders({ 'Authorization': `Bearer ${token}` });
    const payload = {
      id_restaurante: notif.id_restaurante,
      puntuacion,
      comentarios: this.comentariosTemp[notif.id] || null,
    };

    this.http.post(`${BASE_URL}/calificaciones/`, payload, { headers }).subscribe({
      next: () => {
        this.calificacionesEnviadas[notif.id] = puntuacion;
        sessionStorage.setItem('calificaciones_enviadas', JSON.stringify(this.calificacionesEnviadas));
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error al calificar:', err.error?.detail);
        this.cdr.detectChanges();
      }
    });
  }

  cargarCalificacionesPrevias() {
  const token = this.authService.getToken();
  if (!token) return;
  const headers = new HttpHeaders({ 'Authorization': `Bearer ${token}` });
  this.http.get<any[]>(`${BASE_URL}/calificaciones/mias`, { headers }).subscribe({
    next: (data) => {
      // Marcar como enviadas usando id_restaurante
      data.forEach(c => {
        // Buscar la notificación que corresponde a ese restaurante
        const notif = this.notifSvc.notificaciones().find(
          n => n.id_restaurante === c.id_restaurante
        );
        if (notif) {
          this.calificacionesEnviadas[notif.id] = c.puntuacion;
        }
      });
      this.cdr.detectChanges();
    }
  });
}
}

