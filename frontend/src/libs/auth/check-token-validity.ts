import { type Storage } from '~/libs/storage/types';

const TOKEN_VALIDITY_CHECK_STORAGE_KEY = 'tokenValidityCheckPerformed';

export const checkTokenValidity = async (
  storage: Storage,
  onCheck: () => Promise<void>,
) => {
  if (storage.get(TOKEN_VALIDITY_CHECK_STORAGE_KEY)) {
    return;
  }
  try {
    await onCheck();
  } catch {}
  storage.set(TOKEN_VALIDITY_CHECK_STORAGE_KEY, 'true');
};
