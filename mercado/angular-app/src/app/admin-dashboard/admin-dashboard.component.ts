import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';

const BASE_URL = 'http://localhost:8000';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './admin-dashboard.component.html',
  styleUrl: './admin-dashboard.component.css'
})
export class AdminDashboardComponent implements OnInit {

  vistaActiva: 'restaurantes' | 'solicitudes' = 'solicitudes';
  restaurantes: any[] = [];
  solicitudes: any[] = [];
  loading = false;

  constructor(
    private http: HttpClient,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() { this.cargarDatos(); }

  private get headers() {
    const token = sessionStorage.getItem('admin_token');
    return new HttpHeaders({ 'Authorization': `Bearer ${token}` });
  }

  get adminNombre() { return sessionStorage.getItem('admin_nombre') || 'Admin'; }

  cargarDatos() {
    this.loading = true;
    this.http.get<any[]>(`${BASE_URL}/admin/restaurantes`, { headers: this.headers }).subscribe({
      next: (data) => {
        this.restaurantes = data;
        this.solicitudes = data.filter(r => !r.estado);
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: () => { this.loading = false; this.cdr.detectChanges(); }
    });
  }

  activar(id: number) {
    this.http.patch(`${BASE_URL}/admin/restaurantes/${id}/activar`, {}, { headers: this.headers }).subscribe({
      next: () => this.cargarDatos()
    });
  }

  desactivar(id: number) {
    if (!confirm('¿Desactivar este restaurante?')) return;
    this.http.patch(`${BASE_URL}/admin/restaurantes/${id}/desactivar`, {}, { headers: this.headers }).subscribe({
      next: () => this.cargarDatos()
    });
  }

  logout() {
    sessionStorage.removeItem('admin_token');
    sessionStorage.removeItem('admin_nombre');
    this.router.navigate(['/admin/login']);
  }
}
