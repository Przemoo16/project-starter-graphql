import { expect, test } from 'vitest';

import {
  clearTokens,
  getAuthHeader,
  isAuthorized,
  login,
  logout,
  refreshToken,
} from './user';

class TokenStorage {
  readonly storage = new Map<string, string>();

  get(key: string) {
    return this.storage.get(key) ?? null;
  }

  set(key: string, value: string) {
    this.storage.set(key, value);
  }

  remove(key: string) {
    this.storage.delete(key);
  }
}

test(`[isAuthorized function]: returns true if access token is present`, () => {
  const tokenStorage = new TokenStorage();
  tokenStorage.set('accessToken', 'access-token');

  const authorized = isAuthorized(tokenStorage);

  expect(authorized).toBe(true);
});

test(`[isAuthorized function]: returns true if refresh token is present`, () => {
  const tokenStorage = new TokenStorage();
  tokenStorage.set('refreshToken', 'refresh-token');

  const authorized = isAuthorized(tokenStorage);

  expect(authorized).toBe(true);
});

test(`[isAuthorized function]: returns false if tokens are missing`, () => {
  const tokenStorage = new TokenStorage();

  const authorized = isAuthorized(tokenStorage);

  expect(authorized).toBe(false);
});

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

test(`[clearTokens function]: removes tokens`, () => {
  const tokenStorage = new TokenStorage();
  tokenStorage.set('accessToken', 'access-token');
  tokenStorage.set('refreshToken', 'refresh-token');

  clearTokens(tokenStorage);

  expect(tokenStorage.get('accessToken')).toBeNull();
  expect(tokenStorage.get('refreshToken')).toBeNull();
});

test(`[login function]: saves tokens`, async () => {
  const onRequest = async () => ({
    login: {
      accessToken: 'access-token',
      refreshToken: 'refresh-token',
      tokenType: 'Bearer',
    },
  });
  const tokenStorage = new TokenStorage();

  await login(onRequest, tokenStorage, 'test@email.com', 'testPassword');

  expect(tokenStorage.get('accessToken')).toEqual('access-token');
  expect(tokenStorage.get('refreshToken')).toEqual('refresh-token');
});

test(`[login function]: doesn't save tokens on problems`, async () => {
  const onRequest = async () => ({
    login: {
      problems: [{ message: 'Error' }],
    },
  });
  const tokenStorage = new TokenStorage();

  await login(onRequest, tokenStorage, 'test@email.com', 'testPassword');

  expect(tokenStorage.get('accessToken')).toBeNull();
  expect(tokenStorage.get('refreshToken')).toBeNull();
});

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

test(`[logout function]: removes tokens and called onRedirect`, () => {
  const tokenStorage = new TokenStorage();
  tokenStorage.set('accessToken', 'access-token');
  tokenStorage.set('refreshToken', 'refresh-token');
  let redirectUrlCalled = false;

  const onRedirect = () => {
    redirectUrlCalled = true;
  };

  logout(tokenStorage, onRedirect);

  expect(tokenStorage.get('accessToken')).toBeNull();
  expect(tokenStorage.get('refreshToken')).toBeNull();
  expect(redirectUrlCalled).toBe(true);
});
