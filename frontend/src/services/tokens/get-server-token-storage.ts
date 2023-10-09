import { type Cookie } from '@builder.io/qwik-city';

import { ServerCookiesStorage } from '~/libs/storage/server-cookies-storage';

import { TOKEN_COOKIE_PATH } from './constants';
import { getTokenLifetime } from './get-token-lifetime';

export const getServerTokenStorage = (cookie: Cookie) =>
  new ServerCookiesStorage(cookie, getTokenLifetime(), TOKEN_COOKIE_PATH);
