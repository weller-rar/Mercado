import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router, RouterModule } from '@angular/router';

const BASE_URL = 'https://mercado-production.up.railway.app';

@Component({
  selector: 'app-registro-restaurante',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './registro-restaurante.component.html',
  styleUrl: './registro-restaurante.component.css'
})
export class RegistroRestauranteComponent {
  form: FormGroup;
  isSubmitting = false;
  error = '';
  success = false;

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {
    this.form = this.fb.group({
      id_comercial: ['', [Validators.required, Validators.minLength(4), Validators.pattern('^[a-zA-Z0-9_-]+$')]],
      nombre:       ['', [Validators.required]],
      descripcion:  [''],
      horario:      [''],
      contrasena:   ['', [Validators.required, Validators.minLength(6)]],
      confirmar:    ['', [Validators.required]]
    }, { validators: this.passwordsMatch });
  }

  passwordsMatch(group: FormGroup) {
    const pass = group.get('contrasena')?.value;
    const confirm = group.get('confirmar')?.value;
    return pass === confirm ? null : { noCoinciden: true };
  }

  onSubmit() {
    this.error = '';
    if (this.form.valid) {
      this.isSubmitting = true;
      const { id_comercial, nombre, descripcion, horario, contrasena } = this.form.value;

      this.http.post(`${BASE_URL}/restaurantes/registro`, {
        id_comercial, nombre, descripcion, horario, contrasena
      }).subscribe({
        next: () => {
          this.isSubmitting = false;
          this.success = true;
          this.cdr.detectChanges();
        },
        error: (err) => {
          this.isSubmitting = false;
          if (err.status === 400 && err.error?.detail) {
            this.error = err.error.detail;
          } else {
            this.error = 'Ocurrió un error. Intenta nuevamente.';
          }
          this.cdr.detectChanges();
        }
      });
    } else {
      this.form.markAllAsTouched();
    }
  }
}
