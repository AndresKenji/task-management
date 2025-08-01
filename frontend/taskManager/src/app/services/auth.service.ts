import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject, tap } from 'rxjs';
import { User, LoginRequest, Token } from '../models/user.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly baseUrl = 'http://localhost:8000/api/auth';
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient) {
    this.checkAuthToken();
  }

  private checkAuthToken(): void {
    const token = this.getToken();
    if (token) {
      this.getCurrentUser().subscribe({
        next: (user) => this.currentUserSubject.next(user),
        error: () => this.logout()
      });
    }
  }

  login(credentials: LoginRequest): Observable<Token> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    return this.http.post<Token>(`${this.baseUrl}/token`, formData).pipe(
      tap(response => {
        this.setToken(response.access_token);
        // Obtener información del usuario después del login
        this.getCurrentUser().subscribe({
          next: (user) => this.currentUserSubject.next(user),
          error: (err) => {
            console.error('Error getting user info:', err);
            // Si falla obtener el usuario, limpiar el token
            this.logout();
          }
        });
      })
    );
  }

  // Método alternativo para login con cookies (opcional)
  loginWithCookie(credentials: LoginRequest): Observable<any> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    return this.http.post<any>(`${this.baseUrl}/token-cookie`, formData, {
      withCredentials: true // Para incluir cookies en las requests
    }).pipe(
      tap(response => {
        // Con cookies no necesitamos almacenar token en localStorage
        // Obtener información del usuario después del login
        this.getCurrentUser().subscribe({
          next: (user) => this.currentUserSubject.next(user),
          error: (err) => {
            console.error('Error getting user info:', err);
            this.logout();
          }
        });
      })
    );
  }

  logout(): void {
    localStorage.removeItem('access_token');
    this.currentUserSubject.next(null);

    // Llamada al endpoint de logout del backend para limpiar cookies
    this.http.post(`${this.baseUrl}/logout`, {}, {
      withCredentials: true,
      headers: this.getAuthHeaders()
    }).subscribe({
      next: () => console.log('Logout successful'),
      error: (err) => console.log('Logout error (non-critical):', err)
    });
  }

  getCurrentUser(): Observable<User> {
    return this.http.get<User>(`${this.baseUrl}/users/me`);
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  private setToken(token: string): void {
    localStorage.setItem('access_token', token);
  }

  getAuthHeaders(): HttpHeaders {
    const token = this.getToken();
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  getCurrentUserValue(): User | null {
    return this.currentUserSubject.value;
  }

  // Métodos adicionales basados en los endpoints de tu backend

  // Actualizar perfil del usuario
  updateProfile(userData: { email?: string; full_name?: string }): Observable<User> {
    return this.http.put<User>(`${this.baseUrl}/users/me`, userData, {
      headers: this.getAuthHeaders()
    }).pipe(
      tap(user => {
        this.currentUserSubject.next(user);
      })
    );
  }

  // Cambiar contraseña
  changePassword(passwordData: { current_password: string; new_password: string }): Observable<any> {
    return this.http.post(`${this.baseUrl}/users/me/change-password`, passwordData, {
      headers: this.getAuthHeaders()
    });
  }

  // Métodos para administradores (si el usuario actual es admin)

  // Listar todos los usuarios (solo admin)
  getAllUsers(skip: number = 0, limit: number = 100): Observable<User[]> {
    return this.http.get<User[]>(`${this.baseUrl}/users?skip=${skip}&limit=${limit}`, {
      headers: this.getAuthHeaders()
    });
  }

  // Crear nuevo usuario (solo admin)
  createUser(userData: {
    username: string;
    email: string;
    full_name: string;
    plain_password: string;
  }): Observable<User> {
    return this.http.post<User>(`${this.baseUrl}/users`, userData, {
      headers: this.getAuthHeaders()
    });
  }

  // Habilitar/Deshabilitar usuario (solo admin)
  toggleUserStatus(userId: number): Observable<any> {
    return this.http.patch(`${this.baseUrl}/users/${userId}/toggle-status`, {}, {
      headers: this.getAuthHeaders()
    });
  }

  // Otorgar/Quitar permisos de admin (solo admin)
  toggleAdminStatus(userId: number): Observable<any> {
    return this.http.patch(`${this.baseUrl}/users/${userId}/toggle-admin`, {}, {
      headers: this.getAuthHeaders()
    });
  }

  // Eliminar usuario (solo admin)
  deleteUser(userId: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/users/${userId}`, {
      headers: this.getAuthHeaders()
    });
  }

  // Verificar si el usuario actual es administrador
  isAdmin(): boolean {
    const currentUser = this.getCurrentUserValue();
    return currentUser ? currentUser.is_admin : false;
  }
}
