import { $ } from '@builder.io/qwik';
import { isServer } from '@builder.io/qwik/build';

import { fetchAdapter } from '~/libs/api/fetchers';
import { sendAuthorizedRequest, sendRequest } from '~/libs/api/requests';
import { getApiURL } from '~/libs/api/urls';

import { clearTokens, getAuthHeader, refreshToken } from './user';

export const getTokenStorage = $(() => localStorage);

export const REQUEST_SENDER = $(
  async (query: string, variables?: Record<string, unknown>) => {
    const url = await getApiURL(isServer);
    const tokenStorage = await getTokenStorage();
    return await sendAuthorizedRequest(fetchAdapter, url, {
      query,
      variables,
      getAuthHeader: async () => await getAuthHeader(tokenStorage),
      onUnauthorized: async () =>
        await refreshToken(
          async (query: string, variables?: Record<string, unknown>) =>
            await sendRequest(fetchAdapter, url, { query, variables }),
          tokenStorage,
        ),
      onInvalidTokens: async () => {
        await clearTokens(tokenStorage);
      },
    });
  },
);
