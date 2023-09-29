import { type TokenStorage } from '~/libs/storage/types';

import { clearTokens } from './clear-tokens';

export const logout = (storage: TokenStorage, onRedirect: () => void) => {
  clearTokens(storage);
  onRedirect();
};
