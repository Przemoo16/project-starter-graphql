import { describe, expect, test } from 'vitest';

import { checkTokenValidity } from './check-token-validity';
import { TestStorage } from './test-storage';

describe('[checkTokenValidity function]', () => {
  test(`doesn't perform check if check was already performed`, async () => {
    const storage = new TestStorage();
    storage.set('tokenValidityCheckPerformed', 'true');
    let checkCalled = false;
    const check = async () => {
      checkCalled = true;
    };

    await checkTokenValidity(storage, check);

    expect(checkCalled).toBe(false);
  });

  test(`performs check`, async () => {
    const storage = new TestStorage();
    let checkCalled = false;
    const check = async () => {
      checkCalled = true;
    };

    await checkTokenValidity(storage, check);

    expect(checkCalled).toBe(true);
  });

  test(`performs check and ignores any errors`, async () => {
    const storage = new TestStorage();
    let checkCalled = false;
    const check = async () => {
      checkCalled = true;
      throw new Error();
    };

    await checkTokenValidity(storage, check);

    expect(checkCalled).toBe(true);
  });

  test(`saves the flag to the storage`, async () => {
    const storage = new TestStorage();
    const check = async () => {};

    await checkTokenValidity(storage, check);

    expect(storage.get('tokenValidityCheckPerformed')).toEqual('true');
  });
});
