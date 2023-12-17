import { describe, expect, test } from 'vitest';

import { TestStorage } from '~/tests/storage';

import { isAuthenticated } from './is-authenticated';

describe('[isAuthenticated function]', () => {
  test(`returns true if access token is present`, () => {
    const storage = new TestStorage();
    storage.set('accessToken', 'access-token');

    const authenticated = isAuthenticated(storage);

    expect(authenticated).toBe(true);
  });

  test(`returns true if refresh token is present`, () => {
    const storage = new TestStorage();
    storage.set('refreshToken', 'refresh-token');

    const authenticated = isAuthenticated(storage);

    expect(authenticated).toBe(true);
  });

  test(`returns false if tokens are missing`, () => {
    const storage = new TestStorage();

    const authenticated = isAuthenticated(storage);

    expect(authenticated).toBe(false);
  });
});
