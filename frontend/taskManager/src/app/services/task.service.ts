import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Task, TaskCreate, TaskUpdate, TaskStats } from '../models/task.model';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class TaskService {
  private readonly baseUrl = 'http://localhost:8000/api/task'; // Cambia esta URL por la de tu API

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {}

  private getHeaders(): HttpHeaders {
    return this.authService.getAuthHeaders();
  }

  // Obtener todas las tareas del usuario
  getUserTasks(skip: number = 0, limit: number = 100): Observable<Task[]> {
    return this.http.get<Task[]>(`${this.baseUrl}/?skip=${skip}&limit=${limit}`, {
      headers: this.getHeaders()
    });
  }

  // Obtener todas las tareas (solo admin)
  getAllTasks(skip: number = 0, limit: number = 100): Observable<Task[]> {
    return this.http.get<Task[]>(`${this.baseUrl}/all?skip=${skip}&limit=${limit}`, {
      headers: this.getHeaders()
    });
  }

  // Obtener tarea específica por ID
  getTaskById(taskId: number): Observable<Task> {
    return this.http.get<Task>(`${this.baseUrl}/${taskId}`, {
      headers: this.getHeaders()
    });
  }

  // Crear nueva tarea
  createTask(taskData: TaskCreate): Observable<Task> {
    return this.http.post<Task>(`${this.baseUrl}/`, taskData, {
      headers: this.getHeaders()
    });
  }

  // Actualizar tarea
  updateTask(taskId: number, taskData: TaskUpdate): Observable<Task> {
    return this.http.put<Task>(`${this.baseUrl}/${taskId}`, taskData, {
      headers: this.getHeaders()
    });
  }

  // Marcar/Desmarcar tarea como completada
  toggleTaskCompletion(taskId: number): Observable<Task> {
    return this.http.patch<Task>(`${this.baseUrl}/${taskId}/toggle`, {}, {
      headers: this.getHeaders()
    });
  }

  // Marcar tarea como completada
  completeTask(taskId: number): Observable<Task> {
    return this.http.patch<Task>(`${this.baseUrl}/${taskId}/complete`, {}, {
      headers: this.getHeaders()
    });
  }

  // Eliminar tarea
  deleteTask(taskId: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/${taskId}`, {
      headers: this.getHeaders()
    });
  }

  // Obtener estadísticas de tareas
  getTaskStats(): Observable<TaskStats> {
    return this.http.get<TaskStats>(`${this.baseUrl}/stats/summary`, {
      headers: this.getHeaders()
    });
  }
}
