import { component$, Slot } from '@builder.io/qwik';
import { Link } from '@builder.io/qwik-city';

import { Logo } from '~/components/icons/logo';
import { RouteURL } from '~/libs/api/route-url';

export default component$(() => (
  <main class="flex min-h-screen flex-col items-center justify-center bg-base-200">
    <Link href={RouteURL.Home} aria-label="home">
      <Logo height={100} />
    </Link>
    <div class="card w-11/12 max-w-md bg-base-100 shadow-2xl">
      <div class="card-body gap-5">
        <Slot />
      </div>
    </div>
  </main>
));
