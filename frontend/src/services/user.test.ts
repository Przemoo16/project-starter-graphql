import { expect, test } from 'vitest';

import { clearTokens, getAuthHeader, login, refreshToken } from './user';

class TokenStorage {
  readonly storage = new Map<string, string>();

  getItem(key: string) {
    return this.storage.get(key) ?? null;
  }

  setItem(key: string, value: string) {
    this.storage.set(key, value);
  }

  removeItem(key: string) {
    this.storage.delete(key);
  }
}

test(`[getAuthHeader function]: returns auth header`, async () => {
  const tokenStorage = new TokenStorage();
  tokenStorage.setItem('auth:accessToken', 'access-token');

  const headers = await getAuthHeader(tokenStorage);

  expect(headers).toEqual({ Authorization: 'Bearer access-token' });
});

test(`[getAuthHeader function]: returns empty header`, async () => {
  const tokenStorage = new TokenStorage();

  const headers = await getAuthHeader(tokenStorage);

  expect(headers).toEqual({});
});

test(`[clearTokens function]: removes tokens`, async () => {
  const tokenStorage = new TokenStorage();
  tokenStorage.setItem('auth:accessToken', 'access-token');
  tokenStorage.setItem('auth:refreshToken', 'refresh-token');

  await clearTokens(tokenStorage);

  expect(tokenStorage.getItem('auth:accessToken')).toBeNull();
  expect(tokenStorage.getItem('auth:refreshToken')).toBeNull();
});

test(`[login function]: saves tokens`, async () => {
  const requestSender = async () => ({
    login: {
      accessToken: 'access-token',
      refreshToken: 'refresh-token',
      tokenType: 'Bearer',
    },
  });
  const tokenStorage = new TokenStorage();

  await login(requestSender, tokenStorage, 'test@email.com', 'testPassword');

  expect(tokenStorage.getItem('auth:accessToken')).toEqual('access-token');
  expect(tokenStorage.getItem('auth:refreshToken')).toEqual('refresh-token');
});

test(`[login function]: doesn't save tokens on problems`, async () => {
  const requestSender = async () => ({
    login: {
      problems: [{ message: 'Error' }],
    },
  });
  const tokenStorage = new TokenStorage();

  await login(requestSender, tokenStorage, 'test@email.com', 'testPassword');

  expect(tokenStorage.getItem('auth:accessToken')).toBeNull();
  expect(tokenStorage.getItem('auth:refreshToken')).toBeNull();
});

test(`[refreshToken function]: retrieve refresh token and saves new access token`, async () => {
  let calledVariables: Record<string, unknown> | undefined = {};
  const requestSender = async (
    _query: string,
    variables?: Record<string, unknown>,
  ) => {
    calledVariables = variables;
    return {
      refreshToken: {
        accessToken: 'access-token',
        tokenType: 'Bearer',
      },
    };
  };
  const tokenStorage = new TokenStorage();
  tokenStorage.setItem('auth:refreshToken', 'refresh-token');

  await refreshToken(requestSender, tokenStorage);

  expect(calledVariables).toEqual({ token: 'refresh-token' });
  expect(tokenStorage.getItem('auth:accessToken')).toEqual('access-token');
});
