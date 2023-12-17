import { StorageKey } from '~/libs/auth/storage-key';
import { type Storage } from '~/libs/storage/types';
import { type RefreshTokenResponse } from '~/services/graphql';

import { type RequestSender } from './types';

export const refreshToken = async (
  onRequest: RequestSender,
  storage: Storage,
): Promise<RefreshTokenResponse> => {
  const mutation = `
    mutation RefreshToken($token: String!) {
      refreshToken(token: $token) {
        accessToken
        tokenType
      }
    }
  `;

  const token = storage.get(StorageKey.RefreshToken);
  if (!token) {
    throw new Error('No refresh token in the storage to perform refreshing');
  }
  const { refreshToken } = await onRequest(mutation, {
    token,
  });
  storage.set(StorageKey.AccessToken, refreshToken.accessToken);
  // Write the token again to extend the storage expiration
  storage.set(StorageKey.RefreshToken, token);
  return refreshToken;
};
