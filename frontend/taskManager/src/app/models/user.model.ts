export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  is_admin: boolean;
  disabled: boolean;
  creation_date: string;
  last_login?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface CreateUser {
  username: string;
  email: string;
  full_name: string;
  plain_password: string;
}

export interface UserUpdate {
  email?: string;
  full_name?: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}
