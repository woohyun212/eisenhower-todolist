export enum Quadrant {
  DO = 'DO',
  PLAN = 'PLAN',
  DELEGATE = 'DELEGATE',
  ELIMINATE = 'ELIMINATE'
}

export interface Task {
  id: string;
  title: string;
  quadrant: Quadrant | null;
  completed: boolean;
  confidence: number;
  parsed_datetime: string | null;
  created_at: string;
  updated_at: string;
  user_id: string;
  user_override?: boolean;
}

export interface User {
  id: string;
  email: string;
}
