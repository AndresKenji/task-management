import { Component, EventEmitter, Input, Output, OnChanges } from '@angular/core';
import { Task, TaskUpdate } from 'src/app/models/task.model';

@Component({
  selector: 'app-edit-task-modal',
  templateUrl: './edit-tasks-modal.component.html',
  styleUrls: ['./edit-tasks-modal.component.css']
})
export class EditTaskModalComponent implements OnChanges {
  @Input() show = false;
  @Input() task: Task | null = null;
  @Output() close = new EventEmitter<void>();
  @Output() update = new EventEmitter<TaskUpdate>();

  editTaskData: TaskUpdate = {};

  ngOnChanges(): void {
    if (this.task) {
      this.editTaskData = { ...this.task };
    }
  }

  closeModal(): void {
    this.close.emit();
  }

  updateTask(): void {
    this.update.emit(this.editTaskData);
  }
}
