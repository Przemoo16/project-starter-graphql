import { type Storage } from '~/libs/storage/types';

import { StorageKey } from './storage-key';

export const isAuthenticated = (storage: Storage) => {
  return Boolean(
    storage.get(StorageKey.AccessToken) ?? storage.get(StorageKey.RefreshToken),
  );
};
