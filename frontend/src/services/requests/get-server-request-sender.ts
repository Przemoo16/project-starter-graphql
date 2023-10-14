import { type Cookie } from '@builder.io/qwik-city';

import {
  getServerLogoutRedirection,
  type Redirection,
} from '~/services/auth/get-server-logout-redirection';
import { getServerTokenStorage } from '~/services/tokens/get-server-token-storage';

import { getRequestSender } from './get-request-sender';

export const getServerRequestSender = (
  cookie: Cookie,
  onRedirect: Redirection,
) =>
  getRequestSender(
    getServerTokenStorage(cookie),
    getServerLogoutRedirection(onRedirect),
  );
