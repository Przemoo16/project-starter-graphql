import { expect, test } from 'vitest';

import { isAuthorized } from './is-authorized';
import { TestTokenStorage } from './test-token-storage';

test(`[isAuthorized function]: returns true if access token is present`, () => {
  const tokenStorage = new TestTokenStorage();
  tokenStorage.set('accessToken', 'access-token');

  const authorized = isAuthorized(tokenStorage);

  expect(authorized).toBe(true);
});

test(`[isAuthorized function]: returns true if refresh token is present`, () => {
  const tokenStorage = new TestTokenStorage();
  tokenStorage.set('refreshToken', 'refresh-token');

  const authorized = isAuthorized(tokenStorage);

  expect(authorized).toBe(true);
});

test(`[isAuthorized function]: returns false if tokens are missing`, () => {
  const tokenStorage = new TestTokenStorage();

  const authorized = isAuthorized(tokenStorage);

  expect(authorized).toBe(false);
});
