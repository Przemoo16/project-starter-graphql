import { expect, test } from 'vitest';

import { clearTokens } from './clear-tokens';
import { TokenStorage } from './helpers.test';

test(`[clearTokens function]: removes tokens`, () => {
  const tokenStorage = new TokenStorage();
  tokenStorage.set('accessToken', 'access-token');
  tokenStorage.set('refreshToken', 'refresh-token');

  clearTokens(tokenStorage);

  expect(tokenStorage.get('accessToken')).toBeNull();
  expect(tokenStorage.get('refreshToken')).toBeNull();
});
