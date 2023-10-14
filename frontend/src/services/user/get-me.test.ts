import { expect, test } from 'vitest';

import { getMe } from './get-me';
import { TestStorage } from './test-storage';

test(`[getMe function]: throws error if the user is not authenticated`, async () => {
  const onRequest = async () => ({});
  const storage = new TestStorage();

  await expect(
    async () => await getMe(onRequest, storage),
  ).rejects.toThrowError(Error);
});

test(`[getMe function]: sends request if access token is present`, async () => {
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

test(`[getMe function]: sends request if refresh token is present`, async () => {
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
