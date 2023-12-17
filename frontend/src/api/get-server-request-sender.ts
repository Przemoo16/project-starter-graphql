import {
  type RequestEvent,
  type RequestEventLoader,
} from '@builder.io/qwik-city';

import { getServerLogoutRedirection } from '~/auth/get-server-logout-redirection';
import { getServerTokenStorage } from '~/auth/get-server-token-storage';
import { getServerGraphQLApiUrl } from '~/libs/api/get-server-graphql-api-url';

import { getRequestSender } from './get-request-sender';

export const getServerRequestSender = (
  requestEvent: RequestEvent | RequestEventLoader,
) =>
  getRequestSender(
    getServerGraphQLApiUrl(requestEvent.env),
    getServerTokenStorage(requestEvent.cookie),
    getServerLogoutRedirection(requestEvent.redirect),
  );
