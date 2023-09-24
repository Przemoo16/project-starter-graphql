import { $, component$, useSignal } from '@builder.io/qwik';
import {
  type DocumentHead,
  type RequestEvent,
  useNavigate,
} from '@builder.io/qwik-city';
import { Speak, useTranslate } from 'qwik-speak';

import { RouteURL } from '~/libs/api/urls';
import { onProtectedRoute } from '~/services/auth';
import { getClientTokenStorage } from '~/services/storage';
import { logout } from '~/services/user';

export const head: DocumentHead = {
  title: 'runtime.dashboard.head.title',
};

export const onRequest = async (event: RequestEvent) => {
  await onProtectedRoute(event);
};

export default component$(() => (
  <Speak assets={['account']}>
    <Dashboard />
  </Speak>
));

const Dashboard = component$(() => {
  const t = useTranslate();
  const nav = useNavigate();
  const logoutPending = useSignal(false);

  const onLogout = $(async () => {
    logoutPending.value = true;
    await logout(await getClientTokenStorage());
    logoutPending.value = false;
    await nav(RouteURL.Login, { forceReload: true });
  });

  return (
    <>
      <button onClick$={onLogout} disabled={logoutPending.value}>
        {t('account.logout')}
      </button>
    </>
  );
});
