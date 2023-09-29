import { type RequestEventLoader } from '@builder.io/qwik-city';

import { RouteURL } from '~/libs/api/route-url';

import { REDIRECTION_STATUS_CODE } from './constants';

export const getServerLogoutRedirection =
  (requestEvent: RequestEventLoader) => () => {
    // eslint-disable-next-line @typescript-eslint/no-throw-literal
    throw requestEvent.redirect(REDIRECTION_STATUS_CODE, RouteURL.Login);
  };
