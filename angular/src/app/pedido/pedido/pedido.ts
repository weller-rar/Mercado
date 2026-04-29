import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-pedido',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './pedido.html',
})
export class Pedido {

  restaurantes = [
    {
      id: 1,
      nombre: 'Restaurante A',
      menu: [
        { id: 1, nombre: 'Hamburguesa', precio: 15000 },
        { id: 2, nombre: 'Pizza', precio: 20000 }
      ]
    },
    {
      id: 2,
      nombre: 'Restaurante B',
      menu: [
        { id: 3, nombre: 'Sushi', precio: 25000 },
        { id: 4, nombre: 'Ramen', precio: 18000 }
      ]
    }
  ];

  restauranteSeleccionado: any = null;

  carrito: any[] = [];

  seleccionarRestaurante(restaurante: any) {
    this.restauranteSeleccionado = restaurante;
    this.carrito = [];
  }

  agregar(producto: any) {
    const existe = this.carrito.find(p => p.id === producto.id);

    if (existe) {
      existe.cantidad++;
    } else {
      this.carrito.push({ ...producto, cantidad: 1 });
    }
  }

  eliminar(id: number) {
    this.carrito = this.carrito.filter(item => item.id !== id);
  }

  get total() {
    return this.carrito.reduce((sum, item) =>
      sum + item.precio * item.cantidad, 0
    );
  }

  confirmarPedido() {

    if (!this.restauranteSeleccionado || this.carrito.length === 0) {
      alert("Selecciona un restaurante y agrega productos");
      return;
    }

    const pedido = {
      id_restaurante: this.restauranteSeleccionado.id,
      detalles: this.carrito.map(item => ({
        id_producto: item.id,
        cantidad: item.cantidad
      }))
    };

    console.log("Pedido listo para enviar:", pedido);

    alert("Pedido preparado");

    this.carrito = [];
  }

}