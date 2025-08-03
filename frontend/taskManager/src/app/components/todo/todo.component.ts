import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { TaskService } from '../../services/task.service';
import { AuthService } from '../../services/auth.service';
import { Task, TaskCreate, TaskUpdate } from '../../models/task.model';
import { User } from '../../models/user.model';

@Component({
  selector: 'app-todo',
  templateUrl: './todo.component.html',
  styleUrls: ['./todo.component.css']
})
export class TodoComponent implements OnInit {
  tasks: Task[] = [];
  currentUser: User | null = null;
  loading = false;
  error = '';

  // Para el modal de nueva tarea
  showNewTaskModal = false;
  newTask: TaskCreate = {
    title: '',
    description: ''
  };

  // Para el modal de editar tarea
  showEditTaskModal = false;
  editingTask: Task | null = null;
  editTaskData: TaskUpdate = {};

  constructor(
    private taskService: TaskService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
    });
    this.loadTasks();
  }

  loadTasks(): void {
    this.loading = true;
    this.error = '';

    // Usar el método optimizado que maneja automáticamente admin vs usuario
    this.taskService.getTasksForCurrentUser().subscribe({
      next: (tasks) => {
        this.tasks = tasks;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Error al cargar las tareas';
        this.loading = false;
        console.error('Error loading tasks:', err);
      }
    });
  }

  // Métodos para gestionar tareas
  openNewTaskModal(): void {
    this.showNewTaskModal = true;
    this.newTask = { title: '', description: '' };
  }

  closeNewTaskModal(): void {
    this.showNewTaskModal = false;
  }

  createTask(): void {
    if (!this.newTask.title.trim()) {
      return;
    }

    this.taskService.createTask(this.newTask).subscribe({
      next: () => {
        this.loadTasks();
        this.closeNewTaskModal();
      },
      error: (err) => {
        this.error = 'Error al crear la tarea';
        console.error('Error creating task:', err);
      }
    });
  }

  // Editar tarea
  openEditTaskModal(task: Task): void {
    this.editingTask = task;
    this.editTaskData = {
      title: task.title,
      description: task.description,
      done: task.done
    };
    this.showEditTaskModal = true;
  }

  closeEditTaskModal(): void {
    this.showEditTaskModal = false;
    this.editingTask = null;
  }

  updateTask(): void {
    if (!this.editingTask) return;

    this.taskService.updateTask(this.editingTask.id, this.editTaskData).subscribe({
      next: () => {
        this.loadTasks();
        this.closeEditTaskModal();
      },
      error: (err) => {
        this.error = 'Error al actualizar la tarea';
        console.error('Error updating task:', err);
      }
    });
  }

  // Marcar como completada/no completada
  toggleTaskCompletion(task: Task): void {
    this.taskService.toggleTaskCompletion(task.id).subscribe({
      next: () => {
        this.loadTasks();
      },
      error: (err) => {
        this.error = 'Error al actualizar el estado de la tarea';
        console.error('Error toggling task:', err);
      }
    });
  }

  // Eliminar tarea
  deleteTask(task: Task): void {
    if (confirm(`¿Estás seguro de que quieres eliminar la tarea "${task.title}"?`)) {
      this.taskService.deleteTask(task.id).subscribe({
        next: () => {
          this.loadTasks();
        },
        error: (err) => {
          this.error = 'Error al eliminar la tarea';
          console.error('Error deleting task:', err);
        }
      });
    }
  }


}
