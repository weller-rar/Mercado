import { Routes } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { InicioComponent } from './inicio/inicio.component';
import { LoginRestaurant } from './login-restaurant/login-restaurant';
import { RegistroRestauranteComponent } from './registro-restaurante/registro-restaurante.component';
import { DashboardRestauranteComponent } from './dashboard-restaurante/dashboard-restaurante.component';
import { AdminLoginComponent } from './admin-login/admin-login.component';
import { AdminDashboardComponent } from './admin-dashboard/admin-dashboard.component';
import { adminGuard } from './admin-auth.guard';

export const routes: Routes = [
  { path: 'login',                component: LoginComponent },
  { path: 'login-restaurant',     component: LoginRestaurant },
  { path: 'registro-restaurante', component: RegistroRestauranteComponent },
  { path: 'dashboard',            component: DashboardRestauranteComponent },
  { path: 'inicio',               component: InicioComponent },

  // Rutas admin
  { path: 'admin/login',          component: AdminLoginComponent },
  { path: 'admin/dashboard',      component: AdminDashboardComponent, canActivate: [adminGuard] },
  { path: 'admin',                redirectTo: '/admin/login', pathMatch: 'full' },

  { path: '',                     redirectTo: '/login', pathMatch: 'full' }
];
