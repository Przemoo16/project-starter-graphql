import { describe, expect, test } from 'vitest';

import { TestStorage } from '~/tests/storage';

import { getMe } from './get-me';

describe('[getMe function]', () => {
  test(`throws error if the user is not authenticated`, async () => {
    const onRequest = async () => ({});
    const storage = new TestStorage();

    await expect(
      async () => await getMe(onRequest, storage),
    ).rejects.toThrowError(Error);
  });

  test(`sends request if access token is present`, async () => {
    let onRequestCalled = false;
    const onRequest = async () => {
      onRequestCalled = true;
      return {};
    };
    const storage = new TestStorage();
    storage.set('accessToken', 'access-token');

    await getMe(onRequest, storage);

    expect(onRequestCalled).toBe(true);
  });

  test(`sends request if refresh token is present`, async () => {
    let onRequestCalled = false;
    const onRequest = async () => {
      onRequestCalled = true;
      return {};
    };
    const storage = new TestStorage();
    storage.set('refreshToken', 'refresh-token');

    await getMe(onRequest, storage);

    expect(onRequestCalled).toBe(true);
  });
});
