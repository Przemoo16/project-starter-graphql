import { type Storage } from '~/libs/storage/types';

import {
  ACCESS_TOKEN_STORAGE_KEY,
  REFRESH_TOKEN_STORAGE_KEY,
} from './constants';
import { type RequestSender } from './types';

export const refreshToken = async (
  onRequest: RequestSender,
  storage: Storage,
) => {
  const mutation = `
    mutation RefreshToken($token: String!) {
      refreshToken(token: $token) {
        accessToken
        tokenType
      }
    }
  `;

  const token = storage.get(REFRESH_TOKEN_STORAGE_KEY);
  if (!token) {
    throw new Error('No refresh token in the storage to perform refreshing');
  }
  const { refreshToken } = await onRequest(mutation, {
    token,
  });
  storage.set(ACCESS_TOKEN_STORAGE_KEY, refreshToken.accessToken);
  // Write the token again to extend the storage expiration
  storage.set(REFRESH_TOKEN_STORAGE_KEY, token);
  return refreshToken;
};
