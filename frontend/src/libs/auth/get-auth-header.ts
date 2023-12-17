import { type Storage } from '~/libs/storage/types';

import { StorageKey } from './storage-key';

export const getAuthHeader = (storage: Storage) => {
  const accessToken = storage.get(StorageKey.AccessToken);
  const headers: Record<string, string> = accessToken
    ? { Authorization: `Bearer ${accessToken}` }
    : {};
  return headers;
};
