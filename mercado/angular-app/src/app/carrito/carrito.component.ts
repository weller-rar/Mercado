import { Component, signal, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { CarritoService } from './carrito.service';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';

const BASE_URL = 'http://localhost:8000';

const METODOS = [
  { valor: 'efectivo',      label: 'Efectivo',      icono: '💵', desc: 'Paga en el mostrador al recoger' },
  { valor: 'nequi',         label: 'Nequi',         icono: '📱', desc: 'Pago inmediato — cocina empieza ya' },
  { valor: 'daviplata',     label: 'Daviplata',     icono: '📲', desc: 'Pago inmediato — cocina empieza ya' },
  { valor: 'tarjeta',       label: 'Tarjeta',       icono: '💳', desc: 'Pago inmediato — cocina empieza ya' },
  { valor: 'transferencia', label: 'Transferencia', icono: '🏦', desc: 'Pago inmediato — cocina empieza ya' },
];

@Component({
  selector: 'app-carrito',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './carrito.component.html',
  styleUrl: './carrito.component.css'
})
export class CarritoComponent {

  abierto = false;
  paso: 'carrito' | 'pago' | 'confirmado' = 'carrito';
  metodoPago = '';
  procesando = false;
  error = '';
  transaccionConfirmada: any = null;
  readonly metodos = METODOS;

  constructor(
    public carritoSvc: CarritoService,
    private http: HttpClient,
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  abrir() { this.abierto = true; }
  cerrar() { this.abierto = false; }

  seleccionarMetodo(metodo: string) { this.metodoPago = metodo; }

  irAPago() {
    if (this.carritoSvc.items().length === 0) return;
    this.paso = 'pago';
    this.error = '';
  }

  confirmarPedido() {
    if (!this.metodoPago) { this.error = 'Selecciona un método de pago.'; return; }

    // Verificar que hay token de usuario (no de restaurante)
    const token = this.authService.getToken();
    if (!token) {
      this.error = 'Tu sesión expiró. Vuelve a ingresar tu número de teléfono.';
      this.cdr.detectChanges();
      // Redirigir al login después de 2 segundos
      setTimeout(() => this.router.navigate(['/login']), 2000);
      return;
    }

    this.procesando = true;
    this.error = '';

    const headers = new HttpHeaders({ 'Authorization': `Bearer ${token}` });

    const payload = {
      items: this.carritoSvc.items().map(i => ({ id_producto: i.id_producto, cantidad: i.cantidad })),
      metodo_pago: this.metodoPago,
    };

    this.http.post<any>(`${BASE_URL}/checkout`, payload, { headers }).subscribe({
      next: (res) => {
        this.transaccionConfirmada = res;
        this.carritoSvc.vaciar();
        this.paso = 'confirmado';
        this.procesando = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.procesando = false;
        if (err.status === 401) {
          this.error = 'Tu sesión expiró. Vuelve a ingresar tu número de teléfono.';
          setTimeout(() => this.router.navigate(['/login']), 2000);
        } else {
          this.error = err.error?.detail || 'Error al procesar el pedido.';
        }
        this.cdr.detectChanges();
      }
    });
  }

  nuevoPedido() {
    this.paso = 'carrito';
    this.metodoPago = '';
    this.transaccionConfirmada = null;
    this.abierto = false;
  }

  formatEstado(estado: number): string {
    const map: any = { 1: 'Pendiente de pago', 2: 'En preparación', 3: 'Listo para recoger' };
    return map[estado] || '';
  }
}
