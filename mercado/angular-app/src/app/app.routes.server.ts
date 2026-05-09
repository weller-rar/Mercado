import { RenderMode, ServerRoute } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  { path: 'login',                renderMode: RenderMode.Client },
  { path: 'login-restaurant',     renderMode: RenderMode.Client },
  { path: 'registro-restaurante', renderMode: RenderMode.Client },
  { path: 'dashboard',            renderMode: RenderMode.Client },
  { path: 'inicio',               renderMode: RenderMode.Client },
  { path: 'admin/login',          renderMode: RenderMode.Client },
  { path: 'admin/dashboard',      renderMode: RenderMode.Client },
  { path: '**',                   renderMode: RenderMode.Client },
];
