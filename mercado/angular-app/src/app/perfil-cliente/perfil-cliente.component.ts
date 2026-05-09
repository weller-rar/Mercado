import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { NotificacionesService } from '../notificaciones/notificaciones.service';

const BASE_URL = 'https://mercado-production.up.railway.app';

const ESTADOS: any = {
  1: { texto: 'Pendiente de pago', color: '#d69e2e', bg: '#fffaf0', icono: '⏳' },
  2: { texto: 'En preparación',    color: '#6b7c4a', bg: '#f0f5e8', icono: '🍳' },
  3: { texto: 'Listo para recoger',color: '#38a169', bg: '#f0fff4', icono: '🔔' },
  4: { texto: 'Entregado',         color: '#9e9a93', bg: '#f5f3ef', icono: '✓'  },
  5: { texto: 'Cancelado',         color: '#c53030', bg: '#fff5f5', icono: '✕'  },
};

@Component({
  selector: 'app-perfil-cliente',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './perfil-cliente.component.html',
  styleUrl: './perfil-cliente.component.css'
})
export class PerfilClienteComponent implements OnInit {

  abierto = false;
  pedidos: any[] = [];
  loading = false;
  copiado = '';
  readonly ESTADOS = ESTADOS;

  constructor(
    private http: HttpClient,
    public authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef,
    private notifSvc: NotificacionesService
  ) {}

  ngOnInit() {}

  get telefono(): string {
    return this.authService.getTelefono() || '';
  }

  abrir() {
    this.abierto = true;
    this.cargarPedidos();
  }

  cerrar() { this.abierto = false; }

  cargarPedidos() {
    const token = this.authService.getToken();
    if (!token) return;
    this.loading = true;
    const headers = new HttpHeaders({ 'Authorization': `Bearer ${token}` });
    this.http.get<any[]>(`${BASE_URL}/mis-pedidos`, { headers }).subscribe({
      next: (data) => {
        this.pedidos = data;
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: () => { this.loading = false; this.cdr.detectChanges(); }
    });
  }

  estadoInfo(estado: number) {
    return ESTADOS[estado] || { texto: 'Desconocido', color: '#9e9a93', bg: '#f5f3ef', icono: '?' };
  }

  copiarCodigo(codigo: string) {
    navigator.clipboard.writeText(codigo);
    this.copiado = codigo;
    setTimeout(() => { this.copiado = ''; this.cdr.detectChanges(); }, 2000);
  }

  logout() {
    this.notifSvc.limpiar();
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
