import { $ } from '@builder.io/qwik';
import { isServer } from '@builder.io/qwik/build';
import { type RequestEventLoader } from '@builder.io/qwik-city';

import { fetchAdapter } from '~/libs/api/fetchers';
import { sendAuthorizedRequest, sendRequest } from '~/libs/api/requests';
import { getApiURL } from '~/libs/api/urls';
import { type TokenStorage } from '~/libs/tokens/storage';

import { REDIRECTION_STATUS_CODE } from './auth';
import { getClientTokenStorage, getServerTokenStorage } from './storage';
import { getAuthHeader, logout, refreshToken } from './user';

export const getClientRequestSender = $(async () => {
  return await getRequestSender(
    await getClientTokenStorage(),
    async (url: string) => {
      window.location.assign(url);
    },
  );
});

export const getServerRequestSender = $(async (event: RequestEventLoader) => {
  return await getRequestSender(
    await getServerTokenStorage(event.cookie),
    async (url: string) => {
      // eslint-disable-next-line @typescript-eslint/no-throw-literal
      throw event.redirect(REDIRECTION_STATUS_CODE, url);
    },
  );
});

const getRequestSender = $(
  (storage: TokenStorage, onRedirect: (url: string) => Promise<void>) =>
    async (query: string, variables?: Record<string, unknown>) => {
      const url = await getApiURL(isServer);
      return await sendAuthorizedRequest(fetchAdapter, url, {
        query,
        variables,
        onGetAuthHeader: async () => await getAuthHeader(storage),
        onUnauthorized: async () =>
          await refreshToken(
            async (query: string, variables?: Record<string, unknown>) =>
              await sendRequest(fetchAdapter, url, { query, variables }),
            storage,
          ),
        onInvalidTokens: async () => {
          await logout(storage, onRedirect);
        },
      });
    },
);
