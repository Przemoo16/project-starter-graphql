import { expect, test } from 'vitest';

import { login } from './login';
import { TestTokenStorage } from './test-token-storage';

test(`[login function]: saves tokens`, async () => {
  const onRequest = async () => ({
    login: {
      accessToken: 'access-token',
      refreshToken: 'refresh-token',
      tokenType: 'Bearer',
    },
  });
  const tokenStorage = new TestTokenStorage();

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
  const tokenStorage = new TestTokenStorage();

  await login(onRequest, tokenStorage, 'test@email.com', 'testPassword');

  expect(tokenStorage.get('accessToken')).toBeNull();
  expect(tokenStorage.get('refreshToken')).toBeNull();
});
