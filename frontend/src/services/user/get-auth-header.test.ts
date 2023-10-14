import { expect, test } from 'vitest';

import { getAuthHeader } from './get-auth-header';
import { TestStorage } from './test-storage';

test(`[getAuthHeader function]: returns auth header`, () => {
  const storage = new TestStorage();
  storage.set('accessToken', 'access-token');

  const headers = getAuthHeader(storage);

  expect(headers).toEqual({ Authorization: 'Bearer access-token' });
});

test(`[getAuthHeader function]: returns empty header`, () => {
  const storage = new TestStorage();

  const headers = getAuthHeader(storage);

  expect(headers).toEqual({});
});
