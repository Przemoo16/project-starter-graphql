import { type RequestHandler } from '@builder.io/qwik-city';

import { onAnonymousOnlyRoute } from '~/services/auth/on-anonymous-only-route';

export const onGet: RequestHandler = requestEvent => {
  onAnonymousOnlyRoute(requestEvent);
};
