export interface Task {
  id: number;
  title: string;
  description: string;
  done: boolean;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  done?: boolean;
}

export interface TaskStats {
  total_tasks: number;
  completed_tasks: number;
  pending_tasks: number;
  completion_rate: number;
  scope: string;
}
