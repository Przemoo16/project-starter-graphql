import { $ } from '@builder.io/qwik';
import { type Cookie } from '@builder.io/qwik-city';

import {
  ClientCookiesTokenStorage,
  ServerCookiesTokenStorage,
} from '~/libs/tokens/storage';

const TOKEN_LIFETIME_DAYS = 14;

const getTokenLifetime = $(() => {
  const date = new Date();
  date.setDate(date.getDate() + TOKEN_LIFETIME_DAYS);
  return date;
});

export const getClientTokenStorage = $(
  async () => new ClientCookiesTokenStorage(await getTokenLifetime()),
);

export const getServerTokenStorage = $(
  async (cookie: Cookie) =>
    new ServerCookiesTokenStorage(cookie, await getTokenLifetime()),
);