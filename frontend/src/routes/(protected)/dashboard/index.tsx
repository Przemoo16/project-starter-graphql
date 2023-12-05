import { $, component$, useSignal } from '@builder.io/qwik';
import { type DocumentHead } from '@builder.io/qwik-city';
import { inlineTranslate, useSpeak } from 'qwik-speak';

import { getClientLogoutRedirection } from '~/services/auth/get-client-logout-redirection';
import { getClientTokenStorage } from '~/services/tokens/get-client-token-storage';
import { logout } from '~/services/user/logout';

export const head: DocumentHead = () => {
  const t = inlineTranslate();

  return {
    title: t('head.dashboard.title'),
  };
};

export default component$(() => {
  useSpeak({ assets: ['auth'] });

  return <Dashboard />;
});

const Dashboard = component$(() => {
  const t = inlineTranslate();
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
