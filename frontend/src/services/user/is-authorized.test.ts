import { expect, test } from 'vitest';

import { TokenStorage } from './helpers.test';
import { isAuthorized } from './is-authorized';

test(`[isAuthorized function]: returns true if access token is present`, () => {
  const tokenStorage = new TokenStorage();
  tokenStorage.set('accessToken', 'access-token');

  const authorized = isAuthorized(tokenStorage);

  expect(authorized).toBe(true);
});

test(`[isAuthorized function]: returns true if refresh token is present`, () => {
  const tokenStorage = new TokenStorage();
  tokenStorage.set('refreshToken', 'refresh-token');

  const authorized = isAuthorized(tokenStorage);

  expect(authorized).toBe(true);
});

test(`[isAuthorized function]: returns false if tokens are missing`, () => {
  const tokenStorage = new TokenStorage();

  const authorized = isAuthorized(tokenStorage);

  expect(authorized).toBe(false);
});
