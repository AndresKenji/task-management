import { Component, Input, Output } from '@angular/core';
import { Task } from 'src/app/models/task.model';
import { AuthService } from 'src/app/services/auth.service';
import { TaskService } from 'src/app/services/task.service';

@Component({
  selector: 'app-task-card',
  templateUrl: './task-card.component.html',
  styleUrls: ['./task-card.component.css']
})
export class TaskCardComponent {
   @Input() task: Task = null!;
   @Output() error: string = '';
   @Output() reload: boolean = false;

     constructor(
       private taskService: TaskService,
       private authService: AuthService,
     ) {}

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

}
