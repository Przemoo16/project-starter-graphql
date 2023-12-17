import { getClientLogoutRedirection } from '~/auth/get-client-logout-redirection';
import { getClientTokenStorage } from '~/auth/get-client-token-storage';
import { getClientGraphQLApiUrl } from '~/libs/api/get-client-graphql-api-url';

import { getRequestSender } from './get-request-sender';

export const getClientRequestSender = () =>
  getRequestSender(
    getClientGraphQLApiUrl(),
    getClientTokenStorage(),
    getClientLogoutRedirection(),
  );
