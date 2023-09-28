import { isServer } from '@builder.io/qwik/build';
import { type RequestEventLoader } from '@builder.io/qwik-city';

import { fetchAdapter } from '~/libs/api/fetchers';
import { sendAuthorizedRequest, sendRequest } from '~/libs/api/requests';
import { getApiURL } from '~/libs/api/urls';
import { type TokenStorage } from '~/libs/tokens/storage';

import { getClientLogoutRedirection, getServerLogoutRedirection } from './auth';
import { getClientTokenStorage, getServerTokenStorage } from './storage';
import { getAuthHeader, logout, refreshToken } from './user';

export const getClientRequestSender = () =>
  getRequestSender(getClientTokenStorage(), getClientLogoutRedirection());

export const getServerRequestSender = (requestEvent: RequestEventLoader) =>
  getRequestSender(
    getServerTokenStorage(requestEvent.cookie),
    getServerLogoutRedirection(requestEvent),
  );

const getRequestSender =
  (storage: TokenStorage, onRedirect: () => void) =>
  async (query: string, variables?: Record<string, unknown>) => {
    const url = getApiURL(isServer);
    return await sendAuthorizedRequest(fetchAdapter, url, {
      query,
      variables,
      onGetAuthHeader: () => getAuthHeader(storage),
      onUnauthorized: async () =>
        await refreshToken(
          async (query: string, variables?: Record<string, unknown>) =>
            await sendRequest(fetchAdapter, url, { query, variables }),
          storage,
        ),
      onInvalidTokens: () => {
        logout(storage, onRedirect);
      },
    });
  };
