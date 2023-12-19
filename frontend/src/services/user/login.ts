import { hasProblems } from '~/libs/api/has-problems';
import { StorageKey } from '~/libs/auth/storage-key';
import { type Storage } from '~/libs/storage/types';
import { type LoginResponse } from '~/services/graphql';

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

  const { login } = (await onRequest(mutation, {
    input: {
      username: email,
      password,
    },
  })) as { login: LoginResponse };
  if (!hasProblems(login)) {
    storage.set(StorageKey.AccessToken, login.accessToken);
    storage.set(StorageKey.RefreshToken, login.refreshToken);
  }
  return login;
};
