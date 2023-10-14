import { expect, test } from 'vitest';

import { isAuthenticated } from './is-authenticated';
import { TestStorage } from './test-storage';

test(`[isAuthenticated function]: returns true if access token is present`, () => {
  const storage = new TestStorage();
  storage.set('accessToken', 'access-token');

  const authenticated = isAuthenticated(storage);

  expect(authenticated).toBe(true);
});

test(`[isAuthenticated function]: returns true if refresh token is present`, () => {
  const storage = new TestStorage();
  storage.set('refreshToken', 'refresh-token');

  const authenticated = isAuthenticated(storage);

  expect(authenticated).toBe(true);
});

test(`[isAuthenticated function]: returns false if tokens are missing`, () => {
  const storage = new TestStorage();

  const authenticated = isAuthenticated(storage);

  expect(authenticated).toBe(false);
});
