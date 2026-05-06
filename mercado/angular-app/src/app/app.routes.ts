import { Routes } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { InicioComponent } from './inicio/inicio.component';
import { LoginRestaurant } from './login-restaurant/login-restaurant';
import { RegistroRestauranteComponent } from './registro-restaurante/registro-restaurante.component';
import { DashboardRestauranteComponent } from './dashboard-restaurante/dashboard-restaurante.component';

export const routes: Routes = [
  { path: 'login',                component: LoginComponent },
  { path: 'login-restaurant',     component: LoginRestaurant },
  { path: 'registro-restaurante', component: RegistroRestauranteComponent },
  { path: 'inicio',               component: InicioComponent },
  { path: '',                     redirectTo: '/login', pathMatch: 'full' },
  { path: 'dashboard', component: DashboardRestauranteComponent }
];