import { type Storage } from '~/libs/storage/types';

import { clearTokens } from './clear-tokens';

export const logout = (storage: Storage, onRedirect: () => void) => {
  clearTokens(storage);
  onRedirect();
};
