import { getClientLogoutRedirection } from '~/services/auth/get-client-logout-redirection';
import { getClientTokenStorage } from '~/services/tokens/get-client-token-storage';

import { getClientGraphQLApiUrl } from './get-client-graphql-api-url';
import { getRequestSender } from './get-request-sender';

export const getClientRequestSender = () =>
  getRequestSender(
    getClientGraphQLApiUrl(),
    getClientTokenStorage(),
    getClientLogoutRedirection(),
  );
