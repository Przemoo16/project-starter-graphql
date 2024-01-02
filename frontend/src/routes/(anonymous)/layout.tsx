import { component$, Slot } from '@builder.io/qwik';

import { Drawer } from '~/components/anonymous/drawer/drawer';
import { Header } from '~/components/anonymous/header/header';
import { Footer } from '~/components/common/footer/footer';
import { useServerTime } from '~/routes/layout';

export default component$(() => {
  const serverTime = useServerTime();

  return (
    <Drawer>
      <div class="flex h-px min-h-screen flex-col">
        <Header />
        <main class="flex-1">
          <Slot />
        </main>
        <Footer year={serverTime.value.date.getUTCFullYear()} />
      </div>
    </Drawer>
  );
});
