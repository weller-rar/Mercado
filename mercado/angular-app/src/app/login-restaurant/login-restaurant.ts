import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from '../services/auth.service';
import { Router, RouterModule } from '@angular/router';

@Component({
  selector: 'app-login-restaurant',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './login-restaurant.html',
  styleUrl: './login-restaurant.css',
})
export class LoginRestaurant {
  loginForm: FormGroup;
  isSubmitting = false;
  loginError = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {
    this.loginForm = this.fb.group({
      id_comercial: ['', [Validators.required]],
      contrasena:   ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  onSubmit() {
    this.loginError = '';
    if (this.loginForm.valid) {
      this.isSubmitting = true;
      const { id_comercial, contrasena } = this.loginForm.value;

      this.authService.loginRestaurante(id_comercial, contrasena).subscribe({
        next: () => {
          this.isSubmitting = false;
          this.router.navigate(['/dashboard']);
        },
        error: (err) => {
          this.isSubmitting = false;
          if (err.status === 401) {
            this.loginError = 'ID comercial o contraseña incorrectos.';
          } else if (err.status === 403) {
            this.loginError = 'Tu restaurante aún no ha sido activado. Contacta al administrador.';
          } else {
            this.loginError = 'Ocurrió un error. Intenta más tarde.';
          }
          this.cdr.detectChanges();
        }
      });
    } else {
      this.loginForm.markAllAsTouched();
    }
  }
}
