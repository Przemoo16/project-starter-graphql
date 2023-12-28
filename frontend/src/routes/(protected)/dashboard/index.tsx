import { $, component$, useSignal } from '@builder.io/qwik';
import { type DocumentHead } from '@builder.io/qwik-city';
import { inlineTranslate, useSpeak } from 'qwik-speak';

import { getClientLogoutRedirection } from '~/auth/get-client-logout-redirection';
import { getClientTokenStorage } from '~/auth/get-client-token-storage';
import { LoadingButton } from '~/components/common/loading-button/loading-button';
import { logout } from '~/services/user/logout';

export const head: DocumentHead = () => {
  const t = inlineTranslate();

  return {
    title: t('app.head.dashboard.title'),
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
      <LoadingButton onClick$={onLogout} loading={logoutPending.value}>
        {t('auth.logout')}
      </LoadingButton>
    </>
  );
});
