import { expect, test } from 'vitest';

import { TestStorage } from '~/tests/storage';

import { logout } from './logout';

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
