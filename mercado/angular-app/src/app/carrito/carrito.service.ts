import { Injectable, signal, computed } from '@angular/core';

export interface ItemCarrito {
  id_producto: number;
  nombre: string;
  precio: number;
  imagen_url?: string;
  id_restaurante: number;
  nombre_restaurante: string;
  cantidad: number;
}

@Injectable({ providedIn: 'root' })
export class CarritoService {

  private _items = signal<ItemCarrito[]>([]);

  readonly items = this._items.asReadonly();

  readonly total = computed(() =>
    this._items().reduce((s, i) => s + i.precio * i.cantidad, 0)
  );

  readonly totalItems = computed(() =>
    this._items().reduce((s, i) => s + i.cantidad, 0)
  );

  readonly restaurantes = computed(() => {
    const mapa = new Map<number, string>();
    this._items().forEach(i => mapa.set(i.id_restaurante, i.nombre_restaurante));
    return Array.from(mapa.entries()).map(([id, nombre]) => ({ id, nombre }));
  });

  agregar(item: Omit<ItemCarrito, 'cantidad'>) {
    this._items.update(items => {
      const idx = items.findIndex(i => i.id_producto === item.id_producto);
      if (idx >= 0) {
        const copia = [...items];
        copia[idx] = { ...copia[idx], cantidad: copia[idx].cantidad + 1 };
        return copia;
      }
      return [...items, { ...item, cantidad: 1 }];
    });
  }

  reducir(id_producto: number) {
    this._items.update(items => {
      const idx = items.findIndex(i => i.id_producto === id_producto);
      if (idx < 0) return items;
      const copia = [...items];
      if (copia[idx].cantidad <= 1) {
        copia.splice(idx, 1);
      } else {
        copia[idx] = { ...copia[idx], cantidad: copia[idx].cantidad - 1 };
      }
      return copia;
    });
  }

  eliminar(id_producto: number) {
    this._items.update(items => items.filter(i => i.id_producto !== id_producto));
  }

  vaciar() {
    this._items.set([]);
  }

  cantidadDeProducto(id_producto: number): number {
    return this._items().find(i => i.id_producto === id_producto)?.cantidad ?? 0;
  }
}
