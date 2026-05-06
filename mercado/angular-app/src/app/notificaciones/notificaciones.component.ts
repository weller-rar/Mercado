import { Component, OnInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NotificacionesService } from './notificaciones.service';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-notificaciones',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './notificaciones.component.html',
  styleUrl: './notificaciones.component.css'
})
export class NotificacionesComponent implements OnInit, OnDestroy {

  abierto = false;

  constructor(
    public notifSvc: NotificacionesService,
    private authService: AuthService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    if (this.authService.isLoggedIn()) {
      this.notifSvc.iniciarPolling();
    }
  }

  ngOnDestroy() {
    this.notifSvc.detenerPolling();
  }

  abrir() {
    this.abierto = true;
    this.notifSvc.marcarTodasLeidas();
  }

  cerrar() { this.abierto = false; }

  formatFecha(iso: string): string {
    const d = new Date(iso);
    return d.toLocaleDateString('es-CO', { day: '2-digit', month: 'short' }) +
           ' · ' + d.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
  }
}
