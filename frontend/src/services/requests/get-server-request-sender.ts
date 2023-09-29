import { type RequestEventLoader } from '@builder.io/qwik-city';

import { getServerLogoutRedirection } from '~/services/auth/get-server-logout-redirection';
import { getServerTokenStorage } from '~/services/tokens/get-server-token-storage';

import { getRequestSender } from './get-request-sender';

export const getServerRequestSender = (requestEvent: RequestEventLoader) =>
  getRequestSender(
    getServerTokenStorage(requestEvent.cookie),
    getServerLogoutRedirection(requestEvent),
  );
