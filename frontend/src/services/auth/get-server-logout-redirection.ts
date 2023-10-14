import { type RedirectMessage } from '@builder.io/qwik-city/middleware/request-handler';

import { RouteURL } from '~/libs/api/route-url';

import { REDIRECTION_STATUS_CODE } from './constants';

type RedirectCode = 300 | 301 | 302 | 303 | 304 | 305 | 307 | 308;

export type Redirection = (
  statusCode: RedirectCode,
  url: string,
) => RedirectMessage;

export const getServerLogoutRedirection = (onRedirect: Redirection) => () => {
  // eslint-disable-next-line @typescript-eslint/no-throw-literal
  throw onRedirect(REDIRECTION_STATUS_CODE, RouteURL.Login);
};
