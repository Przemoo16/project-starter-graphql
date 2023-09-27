import { $, component$, useSignal } from '@builder.io/qwik';
import { type DocumentHead, type RequestEvent } from '@builder.io/qwik-city';
import { Speak, useTranslate } from 'qwik-speak';

import { onProtectedRoute } from '~/services/auth';
import { getClientTokenStorage } from '~/services/storage';
import { logout } from '~/services/user';

export const head: DocumentHead = {
  title: 'runtime.dashboard.head.title',
};

export const onRequest = async (requestEvent: RequestEvent) => {
  await onProtectedRoute(requestEvent);
};

export default component$(() => (
  <Speak assets={['account']}>
    <Dashboard />
  </Speak>
));

const Dashboard = component$(() => {
  const t = useTranslate();
  const logoutPending = useSignal(false);

  const onLogout = $(async () => {
    logoutPending.value = true;
    await logout(await getClientTokenStorage(), async (url: string) => {
      window.location.assign(url);
    });
    logoutPending.value = false;
  });

  return (
    <>
      <button onClick$={onLogout} disabled={logoutPending.value}>
        {t('account.logout')}
      </button>
    </>
  );
});
