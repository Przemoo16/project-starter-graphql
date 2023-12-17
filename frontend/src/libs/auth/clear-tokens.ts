import { type Storage } from '~/libs/storage/types';

import { StorageKey } from './storage-key';

export const clearTokens = (storage: Storage) => {
  storage.remove(StorageKey.AccessToken);
  storage.remove(StorageKey.RefreshToken);
};
