import { expect, test } from 'vitest';

import { logout } from './logout';
import { TestTokenStorage } from './test-token-storage';

test(`[logout function]: removes tokens and called onRedirect`, () => {
  const tokenStorage = new TestTokenStorage();
  tokenStorage.set('accessToken', 'access-token');
  tokenStorage.set('refreshToken', 'refresh-token');
  let redirectUrlCalled = false;

  const onRedirect = () => {
    redirectUrlCalled = true;
  };

  logout(tokenStorage, onRedirect);

  expect(tokenStorage.get('accessToken')).toBeNull();
  expect(tokenStorage.get('refreshToken')).toBeNull();
  expect(redirectUrlCalled).toBe(true);
});
