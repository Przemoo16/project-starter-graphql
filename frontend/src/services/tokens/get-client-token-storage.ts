import { ClientCookiesStorage } from '~/libs/storage/client-cookies-storage';

import { TOKEN_COOKIE_PATH } from './constants';
import { getTokenLifetime } from './get-token-lifetime';

export const getClientTokenStorage = () =>
  new ClientCookiesStorage(getTokenLifetime(), TOKEN_COOKIE_PATH);
