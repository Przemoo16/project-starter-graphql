import { expect, test } from 'vitest';

import { clearTokens, login, refreshToken } from './user';

class TokenStorage {
  readonly storage = new Map<string, string>();

  getItem(key: string): string | null {
    return this.storage.get(key) ?? null;
  }

  setItem(key: string, value: string): void {
    this.storage.set(key, value);
  }

  removeItem(key: string): void {
    this.storage.delete(key);
  }
}

test(`[clearTokens function]: removes tokens`, async () => {
  const tokenStorage = new TokenStorage();
  tokenStorage.setItem('auth:accessToken', 'access-token');
  tokenStorage.setItem('auth:refreshToken', 'refresh-token');

  await clearTokens(tokenStorage);

  expect(tokenStorage.getItem('auth:accessToken')).toBeNull();
  expect(tokenStorage.getItem('auth:refreshToken')).toBeNull();
});

test(`[login function]: saves tokens`, async () => {
  const requestSender = async (
    _query: string,
    _variables?: Record<string, unknown>,
  ): Promise<Record<string, unknown>> => {
    return {
      login: {
        accessToken: 'access-token',
        refreshToken: 'refresh-token',
        tokenType: 'Bearer',
      },
    };
  };
  const tokenStorage = new TokenStorage();

  await login(requestSender, tokenStorage, 'test@email.com', 'testPassword');

  expect(tokenStorage.getItem('auth:accessToken')).toEqual('access-token');
  expect(tokenStorage.getItem('auth:refreshToken')).toEqual('refresh-token');
});

test(`[login function]: doesn't save tokens on problems`, async () => {
  const requestSender = async (
    _query: string,
    _variables?: Record<string, unknown>,
  ): Promise<Record<string, unknown>> => {
    return {
      login: {
        problems: [{ message: 'Error' }],
      },
    };
  };
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
  ): Promise<Record<string, unknown>> => {
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
