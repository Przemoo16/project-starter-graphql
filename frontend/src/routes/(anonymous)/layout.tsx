import { component$, Slot } from '@builder.io/qwik';
import { routeLoader$ } from '@builder.io/qwik-city';

import { Drawer } from '~/components/drawer/drawer';
import { Footer } from '~/components/footer/footer';
import { Header } from '~/components/header/header';

export const useServerTimeLoader = routeLoader$(() => ({
  date: new Date(),
}));

export default component$(() => {
  const serverTime = useServerTimeLoader();

  return (
    <Drawer>
      <div class="flex h-px min-h-screen flex-col">
        <Header />
        <main class="flex-1 bg-base-100">
          <Slot />
        </main>
        <Footer year={serverTime.value.date.getUTCFullYear()} />
      </div>
    </Drawer>
  );
});
