import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';

export const adminGuard: CanActivateFn = () => {
  const router = inject(Router);
  const token = sessionStorage.getItem('admin_token');
  if (!token) {
    router.navigate(['/admin/login']);
    return false;
  }
  return true;
};
