import { type TokenStorage } from '~/libs/storage/types';

import {
  ACCESS_TOKEN_STORAGE_KEY,
  REFRESH_TOKEN_STORAGE_KEY,
} from './constants';

export const isAuthorized = (storage: TokenStorage) => {
  return Boolean(
    storage.get(ACCESS_TOKEN_STORAGE_KEY) ??
      storage.get(REFRESH_TOKEN_STORAGE_KEY),
  );
};
