import { $ } from '@builder.io/qwik';
import { type RequestEvent } from '@builder.io/qwik-city';

import { RouteURL } from '~/libs/api/urls';

import { getServerTokenStorage } from './storage';
import { isAuthorized } from './user';

const REDIRECTION_STATUS_CODE = 302;

export const onProtectedRoute = $(async (event: RequestEvent) => {
  const authorized = await isAuthorized(
    await getServerTokenStorage(event.cookie),
  );
  if (!authorized) {
    // eslint-disable-next-line @typescript-eslint/no-throw-literal
    throw event.redirect(
      REDIRECTION_STATUS_CODE,
      `${RouteURL.Login}?callbackUrl=${event.url.pathname}`,
    );
  }
});

export const onOnlyAnonymousRoute = $(async (event: RequestEvent) => {
  const authorized = await isAuthorized(
    await getServerTokenStorage(event.cookie),
  );
  if (authorized) {
    // eslint-disable-next-line @typescript-eslint/no-throw-literal
    throw event.redirect(REDIRECTION_STATUS_CODE, RouteURL.Dashboard);
  }
});
