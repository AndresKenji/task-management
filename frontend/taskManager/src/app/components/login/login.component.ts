import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { LoginRequest } from '../../models/user.model';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  loginData: LoginRequest = {
    username: '',
    password: ''
  };

  loading = false;
  error = '';

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  onSubmit(): void {
    if (!this.loginData.username || !this.loginData.password) {
      this.error = 'Por favor, completa todos los campos';
      return;
    }

    this.loading = true;
    this.error = '';

    this.authService.login(this.loginData).subscribe({
      next: () => {
        this.loading = false;
        this.router.navigate(['/tasks']);
      },
      error: (err) => {
        this.loading = false;
        this.error = err.error?.detail || 'Error al iniciar sesión';
      }
    });
  }

  // Método para simular diferentes acciones - estos son los links que puedes cambiar
  navigateToRegister(): void {
    // Aquí irías a la página de registro
    console.log('Navegar a registro - cambiar por tu lógica');
  }

  forgotPassword(): void {
    // Aquí irías a la página de recuperación de contraseña
    console.log('Recuperar contraseña - cambiar por tu lógica');
  }
}
