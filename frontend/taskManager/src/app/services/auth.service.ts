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
  private initializationCompleted = false;

  constructor(
    private http: HttpClient,
  ) {
    this.initializeAuthState();
  }

  public isInitializationCompleted(): boolean {
    return this.initializationCompleted;
  }

  private initializeAuthState(): void {
    console.log('AuthService: Iniciando verificación de estado...');
    console.log('AuthService: localStorage contenido:', localStorage.getItem('access_token'));

    const token = this.getToken();
    console.log('AuthService: Token obtenido:', token ? 'Token presente' : 'No hay token');

    if (token) {
      console.log('AuthService: Token encontrado, verificando usuario...');
      this.checkAuthToken();
    } else {
      console.log('AuthService: No hay token almacenado');
      this.currentUserSubject.next(null);
      this.initializationCompleted = true;
    }
  }

  private checkAuthToken(): void {
    if (this.isInitializing) return;

    const token = this.getToken();
    if (token) {
      this.isInitializing = true;
      console.log('AuthService: Verificando token con el servidor...');

      this.getCurrentUser().subscribe({
        next: (user) => {
          console.log('AuthService: Usuario autenticado:', user.username);
          this.currentUserSubject.next(user);
          this.isInitializing = false;
          this.initializationCompleted = true;
        },
        error: (err) => {
          console.log('AuthService: Token inválido o expirado, cerrando sesión:', err);
          this.logout();
          this.isInitializing = false;
          this.initializationCompleted = true;
        }
      });
    } else {
      console.log('AuthService: No hay token, estableciendo usuario como null');
      this.currentUserSubject.next(null);
      this.initializationCompleted = true;
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
    console.log('logout() llamado');
    localStorage.removeItem('access_token');
    console.log('Token removido del localStorage');
    this.currentUserSubject.next(null);

    // Solo hacer la petición de logout si hay headers válidos
    const token = localStorage.getItem('access_token'); // Verificar si queda algún token
    if (!token) {
      console.log('No hay token para logout en servidor, solo limpieza local');
      return;
    }

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
    const token = localStorage.getItem('access_token');
    // Reducimos los logs para evitar spam
    // console.log('getToken() llamado, resultado:', token ? 'Token encontrado' : 'No hay token');
    return token;
  }

  private setToken(token: string): void {
    console.log('setToken() llamado, guardando token en localStorage');
    localStorage.setItem('access_token', token);
    console.log('Token guardado exitosamente');
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

  // Método para debug - verificar estado completo
  public debugAuthState(): void {
    console.log('=== DEBUG AUTH STATE ===');
    console.log('Token en localStorage:', localStorage.getItem('access_token'));
    console.log('Usuario actual:', this.getCurrentUserValue());
    console.log('Inicialización completada:', this.initializationCompleted);
    console.log('Está inicializando:', this.isInitializing);
    console.log('========================');
  }
}
