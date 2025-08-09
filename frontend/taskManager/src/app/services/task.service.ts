import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Task, TaskCreate, TaskUpdate, TaskStats } from '../models/task.model';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class TaskService {
  private readonly baseUrl = 'http://localhost:8000/api/task';
  // private readonly baseUrl = 'http://api:8000/api/task';

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {}

  private getHeaders(): HttpHeaders {
    return this.authService.getAuthHeaders();
  }

  getUserTasks(skip: number = 0, limit: number = 100): Observable<Task[]> {
    return this.http.get<Task[]>(`${this.baseUrl}/?skip=${skip}&limit=${limit}`, {
      headers: this.getHeaders()
    });
  }

  getAllTasks(skip: number = 0, limit: number = 100): Observable<Task[]> {
    return this.http.get<Task[]>(`${this.baseUrl}/all?skip=${skip}&limit=${limit}`, {
      headers: this.getHeaders()
    });
  }

  getTaskById(taskId: number): Observable<Task> {
    return this.http.get<Task>(`${this.baseUrl}/${taskId}`, {
      headers: this.getHeaders()
    });
  }

  createTask(taskData: TaskCreate): Observable<Task> {
    return this.http.post<Task>(`${this.baseUrl}/`, taskData, {
      headers: this.getHeaders()
    });
  }

  updateTask(taskId: number, taskData: TaskUpdate): Observable<Task> {
    return this.http.put<Task>(`${this.baseUrl}/${taskId}`, taskData, {
      headers: this.getHeaders()
    });
  }

  toggleTaskCompletion(taskId: number): Observable<Task> {
    return this.http.patch<Task>(`${this.baseUrl}/${taskId}/toggle`, {}, {
      headers: this.getHeaders()
    });
  }

  completeTask(taskId: number): Observable<Task> {
    return this.http.patch<Task>(`${this.baseUrl}/${taskId}/complete`, {}, {
      headers: this.getHeaders()
    });
  }

  deleteTask(taskId: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/${taskId}`, {
      headers: this.getHeaders()
    });
  }

  getTaskStats(): Observable<TaskStats> {
    return this.http.get<TaskStats>(`${this.baseUrl}/stats/summary`, {
      headers: this.getHeaders()
    });
  }

  canViewAllTasks(): boolean {
    return this.authService.isAdmin();
  }

  getTasksForCurrentUser(skip: number = 0, limit: number = 100): Observable<Task[]> {
    return this.getUserTasks(skip, limit);
  }
}
