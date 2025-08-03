import { Component } from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { CreateUser } from 'src/app/models/user.model';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent {
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  loading = false;
  error = '';

  newUserForm = new FormGroup({
    username: new FormControl('', [Validators.required, Validators.minLength(6)]),
    email: new FormControl('', [Validators.required, Validators.email]),
    full_name: new FormControl('', [Validators.required, Validators.minLength(3)]),
    plain_password: new FormControl('', [Validators.required, Validators.minLength(8)])
  });

  onSubmit(): void {
    if (this.newUserForm.invalid) {
      this.error = 'Por favor, completa todos los campos correctamente';
      return;
    }

    this.loading = true;
    this.error = '';

    this.authService.createUser(this.newUserForm.value as CreateUser).subscribe({
      next: () => {
        this.loading = false;
        this.router.navigate(['/login']);
      },
      error: (err) => {
        this.loading = false;
        this.error = err.error?.detail || 'Error al crear el usuario';
      }
    })



  }


}
