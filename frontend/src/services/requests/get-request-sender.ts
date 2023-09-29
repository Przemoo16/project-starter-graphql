import { isServer } from '@builder.io/qwik/build';

import { fetchAdapter } from '~/libs/api/fetchers';
import { getApiURL } from '~/libs/api/get-api-url';
import { sendAuthorizedRequest } from '~/libs/api/send-authorized-request';
import { sendRequest } from '~/libs/api/send-request';
import { type TokenStorage } from '~/libs/storage/types';
import { getAuthHeader } from '~/services/user/get-auth-header';
import { logout } from '~/services/user/logout';
import { refreshToken } from '~/services/user/refresh-token';

export const getRequestSender =
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
