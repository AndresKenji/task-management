import { Component, EventEmitter, Input, Output } from '@angular/core';
import { TaskCreate } from 'src/app/models/task.model';

@Component({
  selector: 'app-new-task-modal',
  templateUrl: './new-tasks-modal.component.html',
  styleUrls: ['./new-tasks-modal.component.css']
})
export class NewTaskModalComponent {
  @Input() show = false;
  @Output() close = new EventEmitter<void>();
  @Output() create = new EventEmitter<TaskCreate>();

  newTask: TaskCreate = { title: '', description: '' };

  closeModal(): void {
    this.close.emit(); // Emitir evento para cerrar el modal
  }

  createTask(): void {
    if (this.newTask.title.trim()) {
      this.create.emit(this.newTask); // Emitir evento con los datos de la nueva tarea
      this.newTask = { title: '', description: '' }; // Limpiar el formulario
    }
  }
}