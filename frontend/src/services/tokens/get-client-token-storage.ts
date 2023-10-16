import { ClientCookiesStorage } from '~/libs/storage/client-cookies-storage';

import { getTokenLifetime } from './get-token-lifetime';

export const getClientTokenStorage = () =>
  new ClientCookiesStorage(getTokenLifetime());
