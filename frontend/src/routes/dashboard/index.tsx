import { $, component$, useSignal } from '@builder.io/qwik';
import { type DocumentHead, type RequestEvent } from '@builder.io/qwik-city';
import { Speak, useTranslate } from 'qwik-speak';

import { getClientLogoutRedirection, onProtectedRoute } from '~/services/auth';
import { getClientTokenStorage } from '~/services/storage';
import { logout } from '~/services/user';

export const head: DocumentHead = {
  title: 'runtime.dashboard.head.title',
};

export const onRequest = (requestEvent: RequestEvent) => {
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
