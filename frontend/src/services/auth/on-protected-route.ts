import { type RequestEvent } from '@builder.io/qwik-city';

import { RouteURL } from '~/libs/api/route-url';
import { getServerTokenStorage } from '~/services/tokens/get-server-token-storage';
import { isAuthorized } from '~/services/user/is-authorized';

import { REDIRECTION_STATUS_CODE } from './constants';

export const onProtectedRoute = (requestEvent: RequestEvent) => {
  const authorized = isAuthorized(getServerTokenStorage(requestEvent.cookie));
  if (!authorized) {
    // eslint-disable-next-line @typescript-eslint/no-throw-literal
    throw requestEvent.redirect(
      REDIRECTION_STATUS_CODE,
      `${RouteURL.Login}?callbackUrl=${requestEvent.url.pathname}`,
    );
  }
};
