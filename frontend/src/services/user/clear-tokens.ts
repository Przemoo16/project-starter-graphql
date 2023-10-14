import { type Storage } from '~/libs/storage/types';

import {
  ACCESS_TOKEN_STORAGE_KEY,
  REFRESH_TOKEN_STORAGE_KEY,
} from './constants';

export const clearTokens = (storage: Storage) => {
  storage.remove(ACCESS_TOKEN_STORAGE_KEY);
  storage.remove(REFRESH_TOKEN_STORAGE_KEY);
};
