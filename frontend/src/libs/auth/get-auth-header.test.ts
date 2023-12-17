import { describe, expect, test } from 'vitest';

import { TestStorage } from '~/tests/storage';

import { getAuthHeader } from './get-auth-header';

describe('[getAuthHeader function]', () => {
  test(`returns auth header`, () => {
    const storage = new TestStorage();
    storage.set('accessToken', 'access-token');

    const headers = getAuthHeader(storage);

    expect(headers).toEqual({ Authorization: 'Bearer access-token' });
  });

  test(`returns empty header`, () => {
    const storage = new TestStorage();

    const headers = getAuthHeader(storage);

    expect(headers).toEqual({});
  });
});
