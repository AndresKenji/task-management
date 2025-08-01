import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { User } from '../../models/user.model';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css']
})
export class ProfileComponent implements OnInit {
  currentUser: User | null = null;
  loading = false;
  error = '';
  success = '';

  // Para editar perfil
  editMode = false;
  profileData = {
    email: '',
    full_name: ''
  };

  // Para cambiar contraseña
  showChangePassword = false;
  passwordData = {
    current_password: '',
    new_password: '',
    confirm_password: ''
  };

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
      if (user) {
        this.profileData = {
          email: user.email,
          full_name: user.full_name
        };
      }
    });

    if (!this.currentUser) {
      this.router.navigate(['/login']);
    }
  }

  toggleEditMode(): void {
    this.editMode = !this.editMode;
    this.error = '';
    this.success = '';

    if (this.currentUser && this.editMode) {
      this.profileData = {
        email: this.currentUser.email,
        full_name: this.currentUser.full_name
      };
    }
  }

  updateProfile(): void {
    if (!this.profileData.email || !this.profileData.full_name) {
      this.error = 'Por favor, completa todos los campos';
      return;
    }

    this.loading = true;
    this.error = '';

    this.authService.updateProfile(this.profileData).subscribe({
      next: () => {
        this.loading = false;
        this.editMode = false;
        this.success = 'Perfil actualizado correctamente';
      },
      error: (err) => {
        this.loading = false;
        this.error = err.error?.detail || 'Error al actualizar el perfil';
      }
    });
  }

  toggleChangePassword(): void {
    this.showChangePassword = !this.showChangePassword;
    this.passwordData = {
      current_password: '',
      new_password: '',
      confirm_password: ''
    };
    this.error = '';
    this.success = '';
  }

  changePassword(): void {
    if (!this.passwordData.current_password || !this.passwordData.new_password) {
      this.error = 'Por favor, completa todos los campos';
      return;
    }

    if (this.passwordData.new_password !== this.passwordData.confirm_password) {
      this.error = 'Las contraseñas no coinciden';
      return;
    }

    if (this.passwordData.new_password.length < 6) {
      this.error = 'La nueva contraseña debe tener al menos 6 caracteres';
      return;
    }

    this.loading = true;
    this.error = '';

    this.authService.changePassword({
      current_password: this.passwordData.current_password,
      new_password: this.passwordData.new_password
    }).subscribe({
      next: () => {
        this.loading = false;
        this.showChangePassword = false;
        this.success = 'Contraseña cambiada correctamente';
        this.passwordData = {
          current_password: '',
          new_password: '',
          confirm_password: ''
        };
      },
      error: (err) => {
        this.loading = false;
        this.error = err.error?.detail || 'Error al cambiar la contraseña';
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/tasks']);
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
