import { Component, signal, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { CarritoService } from './carrito.service';
import { AuthService } from '../services/auth.service';

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
    private cdr: ChangeDetectorRef
  ) {}

  abrir() { this.abierto = true; }
  cerrar() { this.abierto = false; }

  private get headers() {
    return new HttpHeaders({ 'Authorization': `Bearer ${this.authService.getToken()}` });
  }

  seleccionarMetodo(metodo: string) { this.metodoPago = metodo; }

  irAPago() {
    if (this.carritoSvc.items().length === 0) return;
    this.paso = 'pago';
    this.error = '';
  }

  confirmarPedido() {
    if (!this.metodoPago) { this.error = 'Selecciona un método de pago.'; return; }
    this.procesando = true;
    this.error = '';

    const payload = {
      items: this.carritoSvc.items().map(i => ({ id_producto: i.id_producto, cantidad: i.cantidad })),
      metodo_pago: this.metodoPago,
    };

    this.http.post<any>(`${BASE_URL}/checkout`, payload, { headers: this.headers }).subscribe({
      next: (res) => {
        this.transaccionConfirmada = res;
        this.carritoSvc.vaciar();
        this.paso = 'confirmado';
        this.procesando = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.procesando = false;
        this.error = err.error?.detail || 'Error al procesar el pedido.';
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

  esEfectivo(metodo: string) { return metodo === 'efectivo'; }

  formatEstado(estado: number): string {
    const map: any = { 1: 'Pendiente de pago', 2: 'En preparación', 3: 'Listo para recoger' };
    return map[estado] || '';
  }
}
