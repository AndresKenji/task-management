import { Component, EventEmitter, Input, Output, OnChanges } from '@angular/core';
import { Task, TaskUpdate } from 'src/app/models/task.model';

@Component({
  selector: 'app-edit-task-modal',
  templateUrl: './edit-tasks-modal.component.html',
  styleUrls: ['./edit-tasks-modal.component.css']
})
export class EditTaskModalComponent implements OnChanges {
  @Input() show = false; // Controla si el modal está visible
  @Input() task: Task | null = null; // Recibe la tarea a editar
  @Output() close = new EventEmitter<void>(); // Evento para cerrar el modal
  @Output() update = new EventEmitter<TaskUpdate>(); // Evento para actualizar la tarea

  editTaskData: TaskUpdate = {};

  ngOnChanges(): void {
    if (this.task) {
      this.editTaskData = { ...this.task }; // Inicializar datos de edición
    }
  }

  closeModal(): void {
    this.close.emit(); // Emitir evento para cerrar el modal
  }

  updateTask(): void {
    this.update.emit(this.editTaskData); // Emitir evento con los datos actualizados
  }
}
