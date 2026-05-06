import { Pipe, PipeTransform } from '@angular/core';

@Pipe({ name: 'filtroEstado', standalone: true })
export class FiltroEstadoPipe implements PipeTransform {
  transform(pedidos: any[], estado: number): any[] {
    if (!pedidos) return [];
    return pedidos.filter(p => p.estado === estado);
  }
}
