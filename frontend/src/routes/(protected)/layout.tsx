import { type RequestHandler } from '@builder.io/qwik-city';

import { onProtectedRoute } from '~/auth/on-protected-route';

export const onGet: RequestHandler = requestEvent => {
  onProtectedRoute(requestEvent);
};
