import { type Storage } from '~/libs/storage/types';

import {
  ACCESS_TOKEN_STORAGE_KEY,
  REFRESH_TOKEN_STORAGE_KEY,
} from './constants';
import { type RequestSender } from './types';

export const login = async (
  onRequest: RequestSender,
  storage: Storage,
  email: string,
  password: string,
) => {
  const mutation = `
      mutation Login($input: LoginInput!) {
        login(input: $input) {
          ... on LoginSuccess {
            accessToken
            refreshToken
          }
          ... on LoginFailure {
            problems {
              __typename
            }
          }
        }
      }
    `;

  const { login } = await onRequest(mutation, {
    input: {
      username: email,
      password,
    },
  });
  if (!login.problems) {
    storage.set(ACCESS_TOKEN_STORAGE_KEY, login.accessToken);
    storage.set(REFRESH_TOKEN_STORAGE_KEY, login.refreshToken);
  }
  return login;
};
