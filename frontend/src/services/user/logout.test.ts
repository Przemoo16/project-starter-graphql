import { expect, test } from 'vitest';

import { logout } from './logout';
import { TestStorage } from './test-storage';

test(`[logout function]: removes tokens and called onRedirect`, () => {
  const storage = new TestStorage();
  storage.set('accessToken', 'access-token');
  storage.set('refreshToken', 'refresh-token');
  let redirectUrlCalled = false;

  const onRedirect = () => {
    redirectUrlCalled = true;
  };

  logout(storage, onRedirect);

  expect(storage.get('accessToken')).toBeNull();
  expect(storage.get('refreshToken')).toBeNull();
  expect(redirectUrlCalled).toBe(true);
});
