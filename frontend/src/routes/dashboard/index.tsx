import { $, component$, useSignal } from '@builder.io/qwik';
import { type DocumentHead, useNavigate } from '@builder.io/qwik-city';
import { Speak, useTranslate } from 'qwik-speak';

import { getClientTokenStorage } from '~/services/storage';
import { logout } from '~/services/user';

export const head: DocumentHead = {
  title: 'runtime.dashboard.head.title',
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
    await nav('/login', { forceReload: true });
  });

  return (
    <>
      <button onClick$={onLogout} disabled={logoutPending.value}>
        {t('account.logout')}
      </button>
    </>
  );
});
