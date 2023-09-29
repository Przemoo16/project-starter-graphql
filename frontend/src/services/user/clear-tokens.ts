import { type TokenStorage } from '~/libs/storage/types';

import {
  ACCESS_TOKEN_STORAGE_KEY,
  REFRESH_TOKEN_STORAGE_KEY,
} from './constants';

export const clearTokens = (storage: TokenStorage) => {
  storage.remove(ACCESS_TOKEN_STORAGE_KEY);
  storage.remove(REFRESH_TOKEN_STORAGE_KEY);
};
