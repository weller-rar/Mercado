import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from '../services/auth.service';
import { Router, RouterModule } from '@angular/router';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {
  loginForm: FormGroup;
  isSubmitting = false;
  loginError = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      telefono: ['', [Validators.required]]
    });
  }

  onSubmit() {
    this.loginError = '';
    if (this.loginForm.valid) {
      this.isSubmitting = true;
      const { telefono } = this.loginForm.value;

      // Login invitado: solo teléfono, sin contraseña
      this.authService.loginInvitado(telefono).subscribe({
        next: () => {
          this.isSubmitting = false;
          this.router.navigate(['/inicio']);
        },
        error: (err) => {
          console.error('Error en login', err);
          this.isSubmitting = false;
          if (err.status === 403) {
            this.loginError = 'Esta cuenta no es de cliente. Usa el acceso de restaurante.';
          } else {
            this.loginError = 'Ocurrió un error. Intenta nuevamente.';
          }
        }
      });
    } else {
      this.loginForm.markAllAsTouched();
    }
  }
}
