import {
  type RequestEvent,
  type RequestEventLoader,
} from '@builder.io/qwik-city';

import { getServerLogoutRedirection } from '~/services/auth/get-server-logout-redirection';
import { getServerTokenStorage } from '~/services/tokens/get-server-token-storage';

import { getRequestSender } from './get-request-sender';
import { getServerGraphQLApiUrl } from './get-server-graphql-api-url';

export const getServerRequestSender = (
  requestEvent: RequestEvent | RequestEventLoader,
) =>
  getRequestSender(
    getServerGraphQLApiUrl(requestEvent.env),
    getServerTokenStorage(requestEvent.cookie),
    getServerLogoutRedirection(requestEvent.redirect),
  );
