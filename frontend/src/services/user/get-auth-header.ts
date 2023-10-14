import { type Storage } from '~/libs/storage/types';

import { ACCESS_TOKEN_STORAGE_KEY } from './constants';

export const getAuthHeader = (storage: Storage) => {
  const accessToken = storage.get(ACCESS_TOKEN_STORAGE_KEY);
  const headers: Record<string, string> = accessToken
    ? { Authorization: `Bearer ${accessToken}` }
    : {};
  return headers;
};
