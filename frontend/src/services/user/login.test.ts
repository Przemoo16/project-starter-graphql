import { describe, expect, test } from 'vitest';

import { TestStorage } from '~/tests/storage';

import { login } from './login';

describe('[login function]', () => {
  test(`saves tokens`, async () => {
    const onRequest = async () => ({
      login: {
        accessToken: 'access-token',
        refreshToken: 'refresh-token',
      },
    });
    const storage = new TestStorage();

    await login(onRequest, storage, 'test@email.com', 'testPassword');

    expect(storage.get('accessToken')).toEqual('access-token');
    expect(storage.get('refreshToken')).toEqual('refresh-token');
  });

  test(`doesn't save tokens on problems`, async () => {
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
});
