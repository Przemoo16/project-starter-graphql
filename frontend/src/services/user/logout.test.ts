import { expect, test } from 'vitest';

import { TokenStorage } from './helpers.test';
import { logout } from './logout';

test(`[logout function]: removes tokens and called onRedirect`, () => {
  const tokenStorage = new TokenStorage();
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
