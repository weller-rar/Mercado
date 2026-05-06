import { Component, OnInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { FiltroEstadoPipe } from './filtro-estado.pipe';

const BASE_URL = 'http://localhost:8000';

const ESTADOS: any = {
  1: { texto: 'Pendiente de pago', color: '#f6ad55', bg: '#fffaf0' },
  2: { texto: 'En preparación',    color: '#6b7c4a', bg: '#f0f5e8' },
  3: { texto: 'Listo ✓',           color: '#38a169', bg: '#f0fff4' },
  4: { texto: 'Entregado',         color: '#9e9a93', bg: '#f5f3ef' },
  5: { texto: 'Cancelado',         color: '#c53030', bg: '#fff5f5' },
};

@Component({
  selector: 'app-dashboard-restaurante',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule, FormsModule, FiltroEstadoPipe],
  templateUrl: './dashboard-restaurante.component.html',
  styleUrl: './dashboard-restaurante.component.css'
})
export class DashboardRestauranteComponent implements OnInit, OnDestroy {

  perfil: any = null;
  menus: any[] = [];
  productosCache: { [id_menu: number]: any[] } = {};
  menuExpandido: number | null = null;
  loading = true;
  error = '';

  vistaActiva: 'dashboard' | 'pedidos' | 'historial' | 'verificador' | 'vista-cliente' = 'dashboard';

  pedidosActivos: any[] = [];
  pedidosAnterioresIds = new Set<number>();
  pollingInterval: any = null;
  readonly ESTADOS = ESTADOS;

  historial: any[] = [];
  loadingHistorial = false;

  codigoVerificador = '';
  resultadoVerificador: any = null;
  errorVerificador = '';
  buscandoOrden = false;

  modalActivo: 'none'|'editarInfo'|'editarNombre'|'nuevoMenu'|'nuevoProducto'|'editarProducto' = 'none';
  menuSeleccionadoParaProducto: number | null = null;
  productoEditando: any = null;
  modalError = '';
  modalGuardando = false;
  bannerPreview: string | null = null;
  bannerFile: File | null = null;
  subiendoBanner = false;
  productoImagenPreview: string | null = null;
  productoImagenFile: File | null = null;

  infoForm!: FormGroup;
  nombreForm!: FormGroup;
  menuForm!: FormGroup;
  productoForm!: FormGroup;

  constructor(
    private http: HttpClient,
    private authService: AuthService,
    private router: Router,
    private fb: FormBuilder,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    if (!this.authService.isRestauranteLoggedIn()) { this.router.navigate(['/login-restaurant']); return; }
    this.inicializarFormularios();
    this.cargarPerfil();
  }

  ngOnDestroy() { this.detenerPolling(); }

  private get headers(): HttpHeaders {
    return new HttpHeaders({ 'Authorization': `Bearer ${this.authService.getRestauranteToken()}` });
  }

  inicializarFormularios() {
    this.infoForm = this.fb.group({ descripcion: [''], horario: [''] });
    this.nombreForm = this.fb.group({ nombre: ['', Validators.required], id_comercial: ['', Validators.required], contrasena: ['', Validators.required] });
    this.menuForm = this.fb.group({ nombre_menu: ['', Validators.required] });
    this.productoForm = this.fb.group({ nombre: ['', Validators.required], descripcion: [''], precio: [0, [Validators.required, Validators.min(0.01)]], disponible: [1] });
  }

  cargarPerfil() {
    this.loading = true;
    this.http.get(`${BASE_URL}/restaurantes/me/perfil`, { headers: this.headers }).subscribe({
      next: (data: any) => {
        this.perfil = data;
        this.infoForm.patchValue({ descripcion: data.descripcion, horario: data.horario });
        this.cargarMenus();
      },
      error: () => { this.loading = false; this.error = 'Error al cargar el perfil.'; this.cdr.detectChanges(); }
    });
  }

  cargarMenus() {
    this.http.get(`${BASE_URL}/restaurantes/me/menus`, { headers: this.headers }).subscribe({
      next: (data: any) => { this.menus = data; this.loading = false; this.cdr.detectChanges(); },
      error: () => { this.loading = false; this.cdr.detectChanges(); }
    });
  }

  iniciarPolling() {
    this.cargarPedidosActivos();
    this.pollingInterval = setInterval(() => this.cargarPedidosActivos(), 6000);
  }

  detenerPolling() {
    if (this.pollingInterval) { clearInterval(this.pollingInterval); this.pollingInterval = null; }
  }

  cargarPedidosActivos() {
    this.http.get<any[]>(`${BASE_URL}/restaurante/pedidos-activos`, { headers: this.headers }).subscribe({
      next: (data) => {
        const nuevosIds = new Set(data.map(p => p.id_pedido));
        data.forEach(p => { p._nuevo = !this.pedidosAnterioresIds.has(p.id_pedido); });
        this.pedidosActivos = data;
        this.pedidosAnterioresIds = nuevosIds;
        this.cdr.detectChanges();
        setTimeout(() => { this.pedidosActivos.forEach(p => p._nuevo = false); this.cdr.detectChanges(); }, 3000);
      }
    });
  }

  cambiarVista(vista: typeof this.vistaActiva) {
    this.vistaActiva = vista;
    if (vista === 'pedidos') { this.iniciarPolling(); }
    else { this.detenerPolling(); }
    if (vista === 'historial') { this.cargarHistorial(); }
  }

  actualizarEstado(id_pedido: number, estado: number) {
    this.http.patch(`${BASE_URL}/restaurante/pedido/${id_pedido}/estado`, { estado }, { headers: this.headers }).subscribe({
      next: () => this.cargarPedidosActivos()
    });
  }

  estadoInfo(estado: number) { return ESTADOS[estado] || { texto: 'Desconocido', color: '#9e9a93', bg: '#f5f3ef' }; }

  cargarHistorial() {
    this.loadingHistorial = true;
    this.http.get<any[]>(`${BASE_URL}/restaurante/historial`, { headers: this.headers }).subscribe({
      next: (data) => { this.historial = data; this.loadingHistorial = false; this.cdr.detectChanges(); },
      error: () => { this.loadingHistorial = false; this.cdr.detectChanges(); }
    });
  }

  totalHistorial() { return this.historial.filter(p => p.estado === 4).reduce((s: number, p: any) => s + (p.total || 0), 0); }

  verificarOrden() {
    if (!this.codigoVerificador.trim()) return;
    this.buscandoOrden = true;
    this.resultadoVerificador = null;
    this.errorVerificador = '';
    this.http.get(`${BASE_URL}/restaurante/verificar/${this.codigoVerificador.trim()}`, { headers: this.headers }).subscribe({
      next: (data) => { this.resultadoVerificador = data; this.buscandoOrden = false; this.cdr.detectChanges(); },
      error: (err) => { this.errorVerificador = err.error?.detail || 'Orden no encontrada.'; this.buscandoOrden = false; this.cdr.detectChanges(); }
    });
  }

  confirmarPagoEfectivo(id_pedido: number) {
    this.actualizarEstado(id_pedido, 2);
    this.resultadoVerificador = { ...this.resultadoVerificador, estado: 2 };
    this.cdr.detectChanges();
  }

  onBannerSeleccionado(event: Event) {
    const input = event.target as HTMLInputElement;
    if (!input.files?.length) return;
    this.bannerFile = input.files[0];
    const reader = new FileReader();
    reader.onload = (e) => { this.bannerPreview = e.target?.result as string; this.cdr.detectChanges(); };
    reader.readAsDataURL(this.bannerFile);
  }

  subirBanner() {
    if (!this.bannerFile) return;
    this.subiendoBanner = true;
    const fd = new FormData(); fd.append('file', this.bannerFile);
    this.http.post<any>(`${BASE_URL}/upload/banner`, fd, { headers: new HttpHeaders({ 'Authorization': `Bearer ${this.authService.getRestauranteToken()}` }) }).subscribe({
      next: (res) => { this.perfil.imagen_url = res.url; this.bannerPreview = null; this.bannerFile = null; this.subiendoBanner = false; this.cdr.detectChanges(); },
      error: () => { this.subiendoBanner = false; this.cdr.detectChanges(); }
    });
  }

  cancelarBanner() { this.bannerPreview = null; this.bannerFile = null; }

  onProductoImagenSeleccionada(event: Event) {
    const input = event.target as HTMLInputElement;
    if (!input.files?.length) return;
    this.productoImagenFile = input.files[0];
    const reader = new FileReader();
    reader.onload = (e) => { this.productoImagenPreview = e.target?.result as string; this.cdr.detectChanges(); };
    reader.readAsDataURL(this.productoImagenFile);
  }

  toggleMenu(id_menu: number) {
    if (this.menuExpandido === id_menu) { this.menuExpandido = null; return; }
    if (this.productosCache[id_menu] !== undefined) { this.menuExpandido = id_menu; return; }
    this.http.get<any[]>(`${BASE_URL}/menus/${id_menu}/productos`).subscribe({
      next: (data) => { this.productosCache[id_menu] = data; this.menuExpandido = id_menu; this.cdr.detectChanges(); }
    });
  }

  toggleDisponibilidad(producto: any) {
    const nuevo = producto.disponible === 1 ? false : true;
    this.http.patch(`${BASE_URL}/productos/${producto.id_producto}/disponibilidad`, { disponible: nuevo }, { headers: this.headers }).subscribe({
      next: (data: any) => { producto.disponible = data.disponible; this.cdr.detectChanges(); }
    });
  }

  guardarInfo() {
    this.modalError = ''; this.modalGuardando = true;
    this.http.put(`${BASE_URL}/restaurantes/me/info`, this.infoForm.value, { headers: this.headers }).subscribe({
      next: (data: any) => { this.perfil = { ...this.perfil, ...data }; this.modalGuardando = false; this.cerrarModal(); this.cdr.detectChanges(); },
      error: () => { this.modalGuardando = false; this.modalError = 'Error al guardar.'; this.cdr.detectChanges(); }
    });
  }

  guardarNombre() {
    this.modalError = '';
    if (this.nombreForm.invalid) { this.nombreForm.markAllAsTouched(); return; }
    this.modalGuardando = true;
    this.http.put(`${BASE_URL}/restaurantes/me/nombre`, this.nombreForm.value, { headers: this.headers }).subscribe({
      next: (data: any) => { this.perfil = { ...this.perfil, nombre: data.nombre }; this.modalGuardando = false; this.cerrarModal(); this.cdr.detectChanges(); },
      error: (err: any) => { this.modalGuardando = false; this.modalError = err.error?.detail || 'Credenciales incorrectas.'; this.cdr.detectChanges(); }
    });
  }

  crearMenu() {
    this.modalError = '';
    if (this.menuForm.invalid) { this.menuForm.markAllAsTouched(); return; }
    this.modalGuardando = true;
    this.http.post(`${BASE_URL}/menus`, { id_restaurante: this.perfil.id_restaurante, nombre_menu: this.menuForm.value.nombre_menu }, { headers: this.headers }).subscribe({
      next: (data: any) => { this.menus.push(data); this.menuForm.reset(); this.modalGuardando = false; this.cerrarModal(); this.cdr.detectChanges(); },
      error: () => { this.modalGuardando = false; this.modalError = 'Error al crear el menú.'; this.cdr.detectChanges(); }
    });
  }

  eliminarMenu(id_menu: number) {
    if (!confirm('¿Eliminar este menú?')) return;
    this.http.delete(`${BASE_URL}/menus/${id_menu}`, { headers: this.headers }).subscribe({
      next: () => { this.menus = this.menus.filter(m => m.id_menu !== id_menu); delete this.productosCache[id_menu]; if (this.menuExpandido === id_menu) this.menuExpandido = null; this.cdr.detectChanges(); }
    });
  }

  abrirNuevoProducto(id_menu: number) { this.menuSeleccionadoParaProducto = id_menu; this.productoForm.reset({ disponible: 1 }); this.productoEditando = null; this.productoImagenPreview = null; this.productoImagenFile = null; this.modalActivo = 'nuevoProducto'; }

  abrirEditarProducto(producto: any) { this.productoEditando = producto; this.productoForm.patchValue({ nombre: producto.nombre, descripcion: producto.descripcion, precio: producto.precio, disponible: producto.disponible }); this.menuSeleccionadoParaProducto = producto.id_menu; this.productoImagenPreview = producto.imagen_url || null; this.productoImagenFile = null; this.modalActivo = 'editarProducto'; }

  guardarProducto() {
    this.modalError = '';
    if (this.productoForm.invalid) { this.productoForm.markAllAsTouched(); return; }
    this.modalGuardando = true;
    const payload = { ...this.productoForm.value, id_menu: this.menuSeleccionadoParaProducto };

    const subirImagen = (producto: any) => {
      if (!this.productoImagenFile) return;
      const fd = new FormData(); fd.append('file', this.productoImagenFile!);
      this.http.post<any>(`${BASE_URL}/upload/producto/${producto.id_producto}`, fd, { headers: new HttpHeaders({ 'Authorization': `Bearer ${this.authService.getRestauranteToken()}` }) }).subscribe({
        next: (res) => { const cache = this.productosCache[this.menuSeleccionadoParaProducto!]; if (cache) { const idx = cache.findIndex((p: any) => p.id_producto === producto.id_producto); if (idx >= 0) cache[idx].imagen_url = res.url; } this.cdr.detectChanges(); }
      });
    };

    if (this.productoEditando) {
      this.http.put(`${BASE_URL}/productos/${this.productoEditando.id_producto}`, payload, { headers: this.headers }).subscribe({
        next: (data: any) => { const cache = this.productosCache[this.menuSeleccionadoParaProducto!]; if (cache) { const idx = cache.findIndex((p: any) => p.id_producto === data.id_producto); if (idx >= 0) cache[idx] = { ...cache[idx], ...data }; } subirImagen(data); this.modalGuardando = false; this.cerrarModal(); this.cdr.detectChanges(); },
        error: () => { this.modalGuardando = false; this.modalError = 'Error al guardar.'; this.cdr.detectChanges(); }
      });
    } else {
      this.http.post(`${BASE_URL}/productos`, payload, { headers: this.headers }).subscribe({
        next: (data: any) => { if (!this.productosCache[this.menuSeleccionadoParaProducto!]) this.productosCache[this.menuSeleccionadoParaProducto!] = []; this.productosCache[this.menuSeleccionadoParaProducto!].push(data); this.menuExpandido = this.menuSeleccionadoParaProducto; subirImagen(data); this.modalGuardando = false; this.cerrarModal(); this.cdr.detectChanges(); },
        error: () => { this.modalGuardando = false; this.modalError = 'Error al crear producto.'; this.cdr.detectChanges(); }
      });
    }
  }

  eliminarProducto(producto: any) {
    if (!confirm(`¿Eliminar "${producto.nombre}"?`)) return;
    this.http.delete(`${BASE_URL}/productos/${producto.id_producto}`, { headers: this.headers }).subscribe({
      next: () => { const cache = this.productosCache[producto.id_menu]; if (cache) this.productosCache[producto.id_menu] = cache.filter((p: any) => p.id_producto !== producto.id_producto); this.cdr.detectChanges(); }
    });
  }

  abrirModal(modal: typeof this.modalActivo) {
    this.modalError = ''; this.modalActivo = modal;
    if (modal === 'editarInfo') this.infoForm.patchValue({ descripcion: this.perfil?.descripcion, horario: this.perfil?.horario });
    if (modal === 'editarNombre') this.nombreForm.patchValue({ nombre: this.perfil?.nombre });
  }

  cerrarModal() { this.modalActivo = 'none'; this.modalError = ''; this.productoImagenPreview = null; this.productoImagenFile = null; }

  logout() { this.detenerPolling(); this.authService.logout(); this.router.navigate(['/login-restaurant']); }
}
