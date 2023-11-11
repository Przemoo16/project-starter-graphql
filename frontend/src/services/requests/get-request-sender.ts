import { fetchAdapter } from '~/libs/api/fetchers';
import { sendGraphQLAuthenticatedRequest } from '~/libs/api/send-graphql-authenticated-request';
import { sendGraphQLRequest } from '~/libs/api/send-graphql-request';
import { type Storage } from '~/libs/storage/types';
import { getAuthHeader } from '~/services/user/get-auth-header';
import { logout } from '~/services/user/logout';
import { refreshToken } from '~/services/user/refresh-token';

export const getRequestSender =
  (url: string, storage: Storage, onRedirect: () => void) =>
  async (query: string, variables?: Record<string, unknown>) => {
    return await sendGraphQLAuthenticatedRequest(fetchAdapter, url, {
      query,
      variables,
      onGetAuthHeader: () => getAuthHeader(storage),
      onUnauthorized: async () =>
        await refreshToken(
          async (query: string, variables?: Record<string, unknown>) =>
            await sendGraphQLRequest(fetchAdapter, url, { query, variables }),
          storage,
        ),
      onInvalidTokens: async () => {
        logout(storage, onRedirect);
      },
    });
  };
