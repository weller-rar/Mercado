import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { CarritoService } from '../carrito/carrito.service';
import { CarritoComponent } from '../carrito/carrito.component';
import { PerfilClienteComponent } from '../perfil-cliente/perfil-cliente.component';
import { NotificacionesComponent } from '../notificaciones/notificaciones.component';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';

const BASE_URL = 'http://localhost:8000';

@Component({
  selector: 'app-inicio',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule, CarritoComponent, PerfilClienteComponent, NotificacionesComponent],
  templateUrl: './inicio.component.html',
  styleUrl: './inicio.component.css'
})
export class InicioComponent implements OnInit {

  restaurantes: any[] = [];
  restauranteFiltrado: any[] = [];
  restauranteSeleccionado: any = null;
  menus: any[] = [];
  productosCache: { [id_menu: number]: any[] } = {};
  indice: { [id_restaurante: number]: string } = {};
  searchText = '';
  loading = true;
  loadingMenus = false;
  resRestaurantes: any[] = [];
  resMenus: any[] = [];
  resProductos: any[] = [];
  buscando = false;
  datosListos = false;
  datos: any[] = [];

  constructor(
    private http: HttpClient,
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef,
    public carritoSvc: CarritoService
  ) {}

  ngOnInit() { this.cargarTodo(); }

  cargarTodo() {
    this.loading = true;
    this.http.get<any[]>(`${BASE_URL}/restaurantes`).subscribe({
      next: (restaurantes) => {
        this.restaurantes = restaurantes;
        this.restauranteFiltrado = restaurantes;
        this.loading = false;
        this.cdr.detectChanges();

        if (restaurantes.length === 0) { this.datosListos = true; return; }

        const menuReqs = restaurantes.map(r =>
          this.http.get<any[]>(`${BASE_URL}/restaurantes/${r.id_comercial}/menus`).pipe(catchError(() => of([])))
        );

        forkJoin(menuReqs).subscribe((todosMenus: any) => {
          const productoReqs: any[] = [];
          const mapeoProd: any[] = [];

          (todosMenus as any[][]).forEach((menus, ri) => {
            const rest = restaurantes[ri];
            menus.forEach((menu: any) => {
              productoReqs.push(this.http.get<any[]>(`${BASE_URL}/menus/${menu.id_menu}/productos`).pipe(catchError(() => of([]))));
              mapeoProd.push({ menuObj: menu, restObj: rest });
            });
          });

          if (productoReqs.length === 0) {
            this.datos = restaurantes.map((r, i) => ({ restaurante: r, menus: (todosMenus as any[][])[i].map((m: any) => ({ menu: m, productos: [] })) }));
            this.datosListos = true;
            this.cdr.detectChanges();
            return;
          }

          forkJoin(productoReqs).subscribe((todosProductos: any) => {
            this.datos = restaurantes.map((r, ri) => {
              const menusRest = (todosMenus as any[][])[ri] || [];
              return {
                restaurante: r,
                menus: menusRest.map((m: any) => {
                  const idx = mapeoProd.findIndex(mp => mp.menuObj.id_menu === m.id_menu);
                  const prods = idx >= 0 ? (todosProductos as any[][])[idx] || [] : [];
                  return { menu: m, productos: prods };
                })
              };
            });
            this.datosListos = true;
            this.cdr.detectChanges();
          });
        });
      },
      error: () => { this.loading = false; this.cdr.detectChanges(); }
    });
  }

  buscar() {
    const q = this.searchText.toLowerCase().trim();
    this.resRestaurantes = []; this.resMenus = []; this.resProductos = [];
    if (!q) { this.buscando = false; return; }
    this.buscando = true;

    this.datos.forEach(({ restaurante, menus }) => {
      if (restaurante.nombre.toLowerCase().includes(q) || (restaurante.descripcion||'').toLowerCase().includes(q))
        this.resRestaurantes.push(restaurante);

      menus.forEach(({ menu, productos }: any) => {
        if (menu.nombre_menu.toLowerCase().includes(q)) this.resMenus.push({ menu, restaurante });
        productos.forEach((p: any) => {
          if (p.nombre.toLowerCase().includes(q) || (p.descripcion||'').toLowerCase().includes(q))
            this.resProductos.push({ producto: p, menu, restaurante });
        });
      });
    });
  }

  limpiarBusqueda() { this.searchText = ''; this.buscando = false; this.resRestaurantes = []; this.resMenus = []; this.resProductos = []; }

  get hayResultados() { return this.resRestaurantes.length > 0 || this.resMenus.length > 0 || this.resProductos.length > 0; }

  abrirRestaurante(restaurante: any) {
    this.limpiarBusqueda();
    this.restauranteSeleccionado = restaurante;
    this.menus = []; this.productosCache = {};
    this.loadingMenus = true;
    window.scrollTo({ top: 0, behavior: 'instant' });

    const datosRest = this.datos.find(d => d.restaurante.id_restaurante === restaurante.id_restaurante);
    if (datosRest) {
      this.menus = datosRest.menus.map((m: any) => m.menu);
      datosRest.menus.forEach((m: any) => {
        this.productosCache[m.menu.id_menu] = m.productos.filter((p: any) => p.disponible === 1);
      });
      this.loadingMenus = false;
      this.cdr.detectChanges();
      return;
    }

    this.http.get<any[]>(`${BASE_URL}/restaurantes/${restaurante.id_comercial}/menus`).subscribe({
      next: (data) => {
        this.menus = data; this.loadingMenus = false;
        data.forEach((menu: any) => {
          this.http.get<any[]>(`${BASE_URL}/menus/${menu.id_menu}/productos`).subscribe({
            next: (prods) => { this.productosCache[menu.id_menu] = prods.filter((p: any) => p.disponible === 1); this.cdr.detectChanges(); }
          });
        });
        this.cdr.detectChanges();
      },
      error: () => { this.loadingMenus = false; this.cdr.detectChanges(); }
    });
  }

  abrirDesdeResultado(restaurante: any) { this.abrirRestaurante(restaurante); }

  volverALista() { this.restauranteSeleccionado = null; window.scrollTo({ top: 0, behavior: 'smooth' }); }

  // ── Carrito ───────────────────────────────────────────────────────────────
  agregar(producto: any) {
    this.carritoSvc.agregar({
      id_producto: producto.id_producto,
      nombre: producto.nombre,
      precio: producto.precio,
      imagen_url: producto.imagen_url,
      id_restaurante: this.restauranteSeleccionado.id_restaurante,
      nombre_restaurante: this.restauranteSeleccionado.nombre,
    });
  }

  cantidad(id_producto: number) { return this.carritoSvc.cantidadDeProducto(id_producto); }

}
