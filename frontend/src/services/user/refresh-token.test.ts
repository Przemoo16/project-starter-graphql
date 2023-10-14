import { expect, test } from 'vitest';

import { refreshToken } from './refresh-token';
import { TestStorage } from './test-storage';

test(`[refreshToken function]: throws error no refresh token is present`, async () => {
  const onRequest = async () => ({
    refreshToken: {
      accessToken: 'access-token',
      tokenType: 'Bearer',
    },
  });
  const storage = new TestStorage();

  await expect(
    async () => await refreshToken(onRequest, storage),
  ).rejects.toThrowError(Error);
});

test(`[refreshToken function]: sends refresh token and saves tokens`, async () => {
  let variablesCalled = null;
  const onRequest = async (
    _query: string,
    variables?: Record<string, unknown>,
  ) => {
    variablesCalled = variables;
    return {
      refreshToken: {
        accessToken: 'access-token',
        tokenType: 'Bearer',
      },
    };
  };
  const setTokensCalled: Array<Record<string, string>> = [];
  class DummyStorage extends TestStorage {
    set = (key: string, value: string) => {
      setTokensCalled.push({ [key]: value });
      this.storage.set(key, value);
    };
  }
  const storage = new DummyStorage();
  storage.set('refreshToken', 'refresh-token');

  await refreshToken(onRequest, storage);

  expect(variablesCalled).toEqual({ token: 'refresh-token' });
  expect(storage.get('accessToken')).toEqual('access-token');
  expect(setTokensCalled).toEqual([
    { refreshToken: 'refresh-token' },
    { accessToken: 'access-token' },
    { refreshToken: 'refresh-token' },
  ]);
});
