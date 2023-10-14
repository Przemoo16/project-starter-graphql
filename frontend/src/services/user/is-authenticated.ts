import { type Storage } from '~/libs/storage/types';

import {
  ACCESS_TOKEN_STORAGE_KEY,
  REFRESH_TOKEN_STORAGE_KEY,
} from './constants';

export const isAuthenticated = (storage: Storage) => {
  return Boolean(
    storage.get(ACCESS_TOKEN_STORAGE_KEY) ??
      storage.get(REFRESH_TOKEN_STORAGE_KEY),
  );
};
