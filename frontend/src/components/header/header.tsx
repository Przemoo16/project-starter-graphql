import { component$ } from '@builder.io/qwik';
import { Link } from '@builder.io/qwik-city';
import { inlineTranslate } from 'qwik-speak';

import { Logo } from '~/components/icons/logo';
import { RouteURL } from '~/libs/api/route-url';

import { Hamburger } from '../icons/hamburger';

export const Header = component$(() => {
  const t = inlineTranslate();

  return (
    <header>
      <div class="mx-auto max-w-6xl bg-base-100 px-3 sm:px-6">
        <nav class="navbar relative justify-center sm:static sm:justify-start">
          <div class="sm:flex-1">
            <Link href={RouteURL.Home} aria-label="home">
              <Logo height={60} />
            </Link>
          </div>
          <div class="absolute right-0 sm:static sm:hidden">
            <label
              for="drawer"
              aria-label="open sidebar"
              class="btn btn-square btn-ghost"
            >
              <Hamburger />
            </label>
          </div>
          <div class="hidden sm:block">
            <ul class="flex gap-2">
              <li>
                <Link href={RouteURL.Login} class="btn btn-ghost">
                  {t('app.ui.login')}
                </Link>
              </li>
              <li>
                <Link
                  href={RouteURL.Register}
                  class="btn btn-outline btn-primary"
                >
                  {t('app.ui.getStarted')}
                </Link>
              </li>
            </ul>
          </div>
        </nav>
      </div>
    </header>
  );
});
