import { expect, test } from 'vitest';

import { getAuthHeader } from './get-auth-header';
import { TokenStorage } from './helpers.test';

test(`[getAuthHeader function]: returns auth header`, () => {
  const tokenStorage = new TokenStorage();
  tokenStorage.set('accessToken', 'access-token');

  const headers = getAuthHeader(tokenStorage);

  expect(headers).toEqual({ Authorization: 'Bearer access-token' });
});

test(`[getAuthHeader function]: returns empty header`, () => {
  const tokenStorage = new TokenStorage();

  const headers = getAuthHeader(tokenStorage);

  expect(headers).toEqual({});
});
