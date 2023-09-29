import { expect, test } from 'vitest';

import { getAuthHeader } from './get-auth-header';
import { TestTokenStorage } from './test-token-storage';

test(`[getAuthHeader function]: returns auth header`, () => {
  const tokenStorage = new TestTokenStorage();
  tokenStorage.set('accessToken', 'access-token');

  const headers = getAuthHeader(tokenStorage);

  expect(headers).toEqual({ Authorization: 'Bearer access-token' });
});

test(`[getAuthHeader function]: returns empty header`, () => {
  const tokenStorage = new TestTokenStorage();

  const headers = getAuthHeader(tokenStorage);

  expect(headers).toEqual({});
});
