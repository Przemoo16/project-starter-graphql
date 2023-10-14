import { expect, test } from 'vitest';

import { clearTokens } from './clear-tokens';
import { TestStorage } from './test-storage';

test(`[clearTokens function]: removes tokens`, () => {
  const storage = new TestStorage();
  storage.set('accessToken', 'access-token');
  storage.set('refreshToken', 'refresh-token');

  clearTokens(storage);

  expect(storage.get('accessToken')).toBeNull();
  expect(storage.get('refreshToken')).toBeNull();
});
