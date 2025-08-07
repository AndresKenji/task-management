import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject, tap, switchMap, map, catchError } from 'rxjs';
import { User, LoginRequest, Token } from '../models/user.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly baseUrl = 'http://localhost:8000/api/auth';
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();
  private isInitializing = false;

  constructor(
    private http: HttpClient,
  ) {}

  private checkAuthToken(): void {
    if (this.isInitializing) return;

    const token = this.getToken();
    if (token) {
      this.isInitializing = true;

      this.getCurrentUser().subscribe({
        next: (user) => {
          this.currentUserSubject.next(user);
          this.isInitializing = false;
          console.log('Usuario autenticado:', user.username);
        },
        error: (err) => {
          console.log('Token inválido o expirado, cerrando sesión:', err);
          this.logout();
          this.isInitializing = false;
        }
      });
    } else {

      this.currentUserSubject.next(null);
    }
  }

  login(credentials: LoginRequest): Observable<Token> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    return this.http.post<Token>(`${this.baseUrl}/token`, formData).pipe(
      tap(response => {
        console.log('Token recibido, guardando...');
        this.setToken(response.access_token);
      }),
      switchMap(response => {

        console.log('Obteniendo información del usuario...');
        return this.getCurrentUser().pipe(
          tap(user => {
            console.log('Usuario obtenido exitosamente:', user.username);
            this.currentUserSubject.next(user);
          }),
          map(() => response),
          catchError(err => {
            console.error('Error getting user info:', err);
            this.logout();
            throw err;
          })
        );
      })
    );
  }

  loginWithCookie(credentials: LoginRequest): Observable<any> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    return this.http.post<any>(`${this.baseUrl}/token-cookie`, formData, {
      withCredentials: true
    }).pipe(
      tap(response => {

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

    this.http.post(`${this.baseUrl}/logout`, {}, {
      withCredentials: true,
      headers: this.getAuthHeaders()
    }).subscribe({
      next: () => console.log('Logout successful'),
      error: (err) => console.log('Logout error (non-critical):', err)
    });
  }

  getCurrentUser(): Observable<User> {
    return this.http.get<User>(`${this.baseUrl}/users/me`, {
      headers: this.getAuthHeaders()
  });
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

  updateProfile(userData: { email?: string; full_name?: string }): Observable<User> {
    return this.http.put<User>(`${this.baseUrl}/users/me`, userData, {
      headers: this.getAuthHeaders()
    }).pipe(
      tap(user => {
        this.currentUserSubject.next(user);
      })
    );
  }

  changePassword(passwordData: { current_password: string; new_password: string }): Observable<any> {
    return this.http.post(`${this.baseUrl}/users/me/change-password`, passwordData, {
      headers: this.getAuthHeaders()
    });
  }


  getAllUsers(skip: number = 0, limit: number = 100): Observable<User[]> {
    return this.http.get<User[]>(`${this.baseUrl}/users?skip=${skip}&limit=${limit}`, {
      headers: this.getAuthHeaders()
    });
  }

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

  toggleUserStatus(userId: number): Observable<any> {
    return this.http.patch(`${this.baseUrl}/users/${userId}/toggle-status`, {}, {
      headers: this.getAuthHeaders()
    });
  }

  toggleAdminStatus(userId: number): Observable<any> {
    return this.http.patch(`${this.baseUrl}/users/${userId}/toggle-admin`, {}, {
      headers: this.getAuthHeaders()
    });
  }

  deleteUser(userId: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/users/${userId}`, {
      headers: this.getAuthHeaders()
    });
  }

  isAdmin(): boolean {
    const currentUser = this.getCurrentUserValue();
    return currentUser ? currentUser.is_admin : false;
  }
}
