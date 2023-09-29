import { expect, test } from 'vitest';

import { TokenStorage } from './helpers.test';
import { login } from './login';

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
