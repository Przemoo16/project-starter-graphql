import { clearTokens } from '~/libs/auth/clear-tokens';
import { type Storage } from '~/libs/storage/types';

export const logout = (storage: Storage, onRedirect: () => void) => {
  clearTokens(storage);
  onRedirect();
};
