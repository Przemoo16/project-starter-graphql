import { expect, test } from 'vitest';

import { login } from './login';
import { TestStorage } from './test-storage';

test(`[login function]: saves tokens`, async () => {
  const onRequest = async () => ({
    login: {
      accessToken: 'access-token',
      refreshToken: 'refresh-token',
      tokenType: 'Bearer',
    },
  });
  const storage = new TestStorage();

  await login(onRequest, storage, 'test@email.com', 'testPassword');

  expect(storage.get('accessToken')).toEqual('access-token');
  expect(storage.get('refreshToken')).toEqual('refresh-token');
});

test(`[login function]: doesn't save tokens on problems`, async () => {
  const onRequest = async () => ({
    login: {
      problems: [{ message: 'Error' }],
    },
  });
  const storage = new TestStorage();

  await login(onRequest, storage, 'test@email.com', 'testPassword');

  expect(storage.get('accessToken')).toBeNull();
  expect(storage.get('refreshToken')).toBeNull();
});
