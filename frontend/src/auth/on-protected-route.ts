import { type RequestEvent } from '@builder.io/qwik-city';

import { RouteURL } from '~/libs/api/route-url';
import { isAuthenticated } from '~/libs/auth/is-authenticated';

import { REDIRECTION_STATUS_CODE } from './constants';
import { getServerTokenStorage } from './get-server-token-storage';

export const onProtectedRoute = (requestEvent: RequestEvent) => {
  const authenticated = isAuthenticated(
    getServerTokenStorage(requestEvent.cookie),
  );
  if (!authenticated) {
    // eslint-disable-next-line @typescript-eslint/no-throw-literal
    throw requestEvent.redirect(
      REDIRECTION_STATUS_CODE,
      `${RouteURL.Login}?callbackUrl=${requestEvent.url.pathname}`,
    );
  }
};
