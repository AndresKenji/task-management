import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(): boolean {
    console.log('AuthGuard: Verificando autenticación...');

    const token = this.authService.getToken();
    const user = this.authService.getCurrentUserValue();

    console.log('AuthGuard: Token existe:', !!token);
    console.log('AuthGuard: Usuario existe:', !!user);

    if (token && user) {
      console.log('AuthGuard: Acceso permitido para:', user.username);
      return true;
    } else {
      console.log('AuthGuard: Redirigiendo al login');
      this.router.navigate(['/login']);
      return false;
    }
  }
}
