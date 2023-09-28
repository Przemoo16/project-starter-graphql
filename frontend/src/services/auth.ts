import { $ } from '@builder.io/qwik';
import {
  type RequestEvent,
  type RequestEventLoader,
} from '@builder.io/qwik-city';

import { RouteURL } from '~/libs/api/urls';

import { getServerTokenStorage } from './storage';
import { isAuthorized } from './user';

export const REDIRECTION_STATUS_CODE = 302;

export const onProtectedRoute = $(async (requestEvent: RequestEvent) => {
  const authorized = await isAuthorized(
    await getServerTokenStorage(requestEvent.cookie),
  );
  if (!authorized) {
    // eslint-disable-next-line @typescript-eslint/no-throw-literal
    throw requestEvent.redirect(
      REDIRECTION_STATUS_CODE,
      `${RouteURL.Login}?callbackUrl=${requestEvent.url.pathname}`,
    );
  }
});

export const onOnlyAnonymousRoute = $(async (requestEvent: RequestEvent) => {
  const authorized = await isAuthorized(
    await getServerTokenStorage(requestEvent.cookie),
  );
  if (authorized) {
    // eslint-disable-next-line @typescript-eslint/no-throw-literal
    throw requestEvent.redirect(REDIRECTION_STATUS_CODE, RouteURL.Dashboard);
  }
});

export const getClientLogoutRedirection = $(() => async () => {
  window.location.assign(RouteURL.Login);
});

export const getServerLogoutRedirection = $(
  (requestEvent: RequestEventLoader) => async () => {
    // eslint-disable-next-line @typescript-eslint/no-throw-literal
    throw requestEvent.redirect(REDIRECTION_STATUS_CODE, RouteURL.Login);
  },
);
