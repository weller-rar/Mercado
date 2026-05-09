import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

const BASE_URL = 'http://localhost:8000';

@Component({
  selector: 'app-admin-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './admin-login.component.html',
  styleUrl: './admin-login.component.css'
})
export class AdminLoginComponent {
  form: FormGroup;
  isSubmitting = false;
  error = '';

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {
    this.form = this.fb.group({
      nombre:    ['', Validators.required],
      contrasena: ['', Validators.required],
    });
  }

  onSubmit() {
    if (this.form.invalid) { this.form.markAllAsTouched(); return; }
    this.isSubmitting = true;
    this.error = '';

    this.http.post<any>(`${BASE_URL}/usuarios/administrador`, this.form.value).subscribe({
      next: (res) => {
        sessionStorage.setItem('admin_token', res.access_token);
        sessionStorage.setItem('admin_nombre', this.form.value.nombre);
        this.router.navigate(['/admin/dashboard']);
      },
      error: (err) => {
        this.isSubmitting = false;
        this.error = err.error?.detail || 'Credenciales incorrectas.';
        this.cdr.detectChanges();
      }
    });
  }
}
