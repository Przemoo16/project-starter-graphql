import { $, component$, useSignal } from '@builder.io/qwik';
import { type DocumentHead, type RequestHandler } from '@builder.io/qwik-city';
import { Speak, useTranslate } from 'qwik-speak';

import { getClientLogoutRedirection } from '~/services/auth/get-client-logout-redirection';
import { onProtectedRoute } from '~/services/auth/on-protected-route';
import { getClientTokenStorage } from '~/services/tokens/get-client-token-storage';
import { logout } from '~/services/user/logout';

export const head: DocumentHead = {
  title: 'runtime.dashboard.head.title',
};

export const onRequest: RequestHandler = requestEvent => {
  onProtectedRoute(requestEvent);
};

export default component$(() => (
  <Speak assets={['auth']}>
    <Dashboard />
  </Speak>
));

const Dashboard = component$(() => {
  const t = useTranslate();
  const logoutPending = useSignal(false);

  const onLogout = $(() => {
    logoutPending.value = true;
    logout(getClientTokenStorage(), getClientLogoutRedirection());
    logoutPending.value = false;
  });

  return (
    <>
      <button onClick$={onLogout} disabled={logoutPending.value}>
        {t('auth.logout')}
      </button>
    </>
  );
});
