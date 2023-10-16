export interface Storage {
  get: (key: string) => string | null;
  set: (key: string, value: string) => void;
  remove: (key: string) => void;
}

export type SameSite = 'strict' | 'lax' | 'none';
