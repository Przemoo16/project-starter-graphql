import { $ } from '@builder.io/qwik';
import { isServer } from '@builder.io/qwik/build';
import { type Cookie } from '@builder.io/qwik-city';

import { fetchAdapter } from '~/libs/api/fetchers';
import { sendAuthorizedRequest, sendRequest } from '~/libs/api/requests';
import { getApiURL } from '~/libs/api/urls';
import { type TokenStorage } from '~/libs/tokens/storage';

import { getClientTokenStorage, getServerTokenStorage } from './storage';
import { clearTokens, getAuthHeader, refreshToken } from './user';

export const getClientRequestSender = $(
  async () => await getRequestSender(await getClientTokenStorage()),
);

export const getServerRequestSender = $(
  async (cookie: Cookie) =>
    await getRequestSender(await getServerTokenStorage(cookie)),
);

const getRequestSender = $(
  (storage: TokenStorage) =>
    async (query: string, variables?: Record<string, unknown>) => {
      const url = await getApiURL(isServer);
      return await sendAuthorizedRequest(fetchAdapter, url, {
        query,
        variables,
        getAuthHeader: async () => await getAuthHeader(storage),
        onUnauthorized: async () =>
          await refreshToken(
            async (query: string, variables?: Record<string, unknown>) =>
              await sendRequest(fetchAdapter, url, { query, variables }),
            storage,
          ),
        onInvalidTokens: async () => {
          await clearTokens(storage);
        },
      });
    },
);
