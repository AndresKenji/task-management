import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { TaskService } from '../../services/task.service';
import { AuthService } from '../../services/auth.service';
import { TaskStats } from '../../models/task.model';
import { User } from '../../models/user.model';

@Component({
  selector: 'app-task-stats',
  templateUrl: './task-stats.component.html',
  styleUrls: ['./task-stats.component.css']
})
export class TaskStatsComponent implements OnInit {
  stats: TaskStats | null = null;
  currentUser: User | null = null;
  loading = false;
  error = '';

  constructor(
    private taskService: TaskService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
    });

    this.loadStats();
  }

  loadStats(): void {
    this.loading = true;
    this.error = '';

    this.taskService.getTaskStats().subscribe({
      next: (stats) => {
        this.stats = stats;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Error al cargar las estadísticas';
        this.loading = false;
        console.error('Error loading stats:', err);
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/tasks']);
  }

  refreshStats(): void {
    this.loadStats();
  }
}
