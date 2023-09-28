import { type Cookie } from '@builder.io/qwik-city';

import {
  ClientCookiesTokenStorage,
  ServerCookiesTokenStorage,
} from '~/libs/tokens/storage';

const TOKEN_LIFETIME_DAYS = 7; // Some browsers cap client-side cookies to 7 days of storage

const getTokenLifetime = () => {
  const date = new Date();
  date.setDate(date.getDate() + TOKEN_LIFETIME_DAYS);
  return date;
};

export const getClientTokenStorage = () =>
  new ClientCookiesTokenStorage(getTokenLifetime());

export const getServerTokenStorage = (cookie: Cookie) =>
  new ServerCookiesTokenStorage(cookie, getTokenLifetime());
