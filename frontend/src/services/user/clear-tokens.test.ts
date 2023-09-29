import { expect, test } from 'vitest';

import { clearTokens } from './clear-tokens';
import { TestTokenStorage } from './test-token-storage';

test(`[clearTokens function]: removes tokens`, () => {
  const tokenStorage = new TestTokenStorage();
  tokenStorage.set('accessToken', 'access-token');
  tokenStorage.set('refreshToken', 'refresh-token');

  clearTokens(tokenStorage);

  expect(tokenStorage.get('accessToken')).toBeNull();
  expect(tokenStorage.get('refreshToken')).toBeNull();
});
