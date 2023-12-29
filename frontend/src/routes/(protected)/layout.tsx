import { $, component$, Slot } from '@builder.io/qwik';
import { type RequestHandler } from '@builder.io/qwik-city';

import { getClientLogoutRedirection } from '~/auth/get-client-logout-redirection';
import { getClientTokenStorage } from '~/auth/get-client-token-storage';
import { onProtectedRoute } from '~/auth/on-protected-route';
import { Footer } from '~/components/common/footer/footer';
import { Header } from '~/components/protected/header/header';
import { useServerTimeLoader } from '~/routes/layout';
import { logout } from '~/services/user/logout';

export const onGet: RequestHandler = requestEvent => {
  onProtectedRoute(requestEvent);
};

export default component$(() => {
  const serverTime = useServerTimeLoader();

  const onLogout = $(async () => {
    logout(getClientTokenStorage(), getClientLogoutRedirection());
  });

  return (
    <div class="flex h-px min-h-screen flex-col">
      <Header onLogout$={onLogout} />
      <main class="flex-1 bg-base-200">
        <Slot />
      </main>
      <Footer year={serverTime.value.date.getUTCFullYear()} />
    </div>
  );
});
