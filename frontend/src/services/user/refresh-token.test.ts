import { expect, test } from 'vitest';

import { TokenStorage } from './helpers.test';
import { refreshToken } from './refresh-token';

test(`[refreshToken function]: throws error if no refresh is not present`, async () => {
  const onRequest = async () => ({
    refreshToken: {
      accessToken: 'access-token',
      tokenType: 'Bearer',
    },
  });
  const tokenStorage = new TokenStorage();

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
  class TestTokenStorage extends TokenStorage {
    set(key: string, value: string) {
      setTokensCalled.push({ [key]: value });
      this.storage.set(key, value);
    }
  }
  const tokenStorage = new TestTokenStorage();
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
