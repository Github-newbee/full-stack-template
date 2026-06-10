export type Permission = {
  code: string;
  description: string;
};

export type Role = {
  id: string;
  name: string;
  description: string;
  permissions: Permission[];
};

export type User = {
  id: string;
  username: string;
  email: string | null;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  roles: Role[];
};

export type Task = {
  id: string;
  name: string;
  status: string;
  progress: number;
  message: string;
  created_at: string;
};

export type Asset = {
  id: string;
  filename: string;
  content_type: string;
  size: number;
  created_at: string;
};

export type PageResponse<T> = {
  items: T[];
  total: number;
  page: number;
  page_size: number;
};
