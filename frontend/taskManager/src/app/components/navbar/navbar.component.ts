import { Component, Input } from '@angular/core';
import { Router } from '@angular/router';
import { User } from '../../models/user.model';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent {
  @Input() currentUser!: User | null;

  constructor(
    private router: Router,
    private authService: AuthService
  ) {}

  // Métodos de navegación - ahora conectados con las rutas reales
  navigateToProfile(): void {
    this.router.navigate(['/profile']);
  }

  navigateToStats(): void {
    this.router.navigate(['/stats']);
  }

  navigateToSettings(): void {
    // Aquí navegarías a configuraciones - puedes crear un componente similar
    console.log('Navegar a configuraciones - crear componente de configuraciones');
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

}
