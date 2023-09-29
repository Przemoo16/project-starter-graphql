import { expect, test } from 'vitest';

import { refreshToken } from './refresh-token';
import { TestTokenStorage } from './test-token-storage';

test(`[refreshToken function]: throws error if no refresh is not present`, async () => {
  const onRequest = async () => ({
    refreshToken: {
      accessToken: 'access-token',
      tokenType: 'Bearer',
    },
  });
  const tokenStorage = new TestTokenStorage();

  await expect(
    async () => await refreshToken(onRequest, tokenStorage),
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
  class DummyTokenStorage extends TestTokenStorage {
    set(key: string, value: string) {
      setTokensCalled.push({ [key]: value });
      this.storage.set(key, value);
    }
  }

  const tokenStorage = new DummyTokenStorage();
  tokenStorage.set('refreshToken', 'refresh-token');

  await refreshToken(onRequest, tokenStorage);

  expect(variablesCalled).toEqual({ token: 'refresh-token' });
  expect(tokenStorage.get('accessToken')).toEqual('access-token');
  expect(setTokensCalled).toEqual([
    { refreshToken: 'refresh-token' },
    { accessToken: 'access-token' },
    { refreshToken: 'refresh-token' },
  ]);
});
