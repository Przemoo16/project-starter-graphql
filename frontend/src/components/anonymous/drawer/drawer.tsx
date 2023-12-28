import { component$, Slot } from '@builder.io/qwik';
import { Link } from '@builder.io/qwik-city';
import { inlineTranslate } from 'qwik-speak';

import { RouteURL } from '~/libs/api/route-url';

export const Drawer = component$(() => {
  const t = inlineTranslate();

  return (
    <div class="drawer">
      <input id="drawer" type="checkbox" class="drawer-toggle" />
      <div class="drawer-content">
        <Slot />
      </div>
      <div class="drawer-side">
        <label
          for="drawer"
          aria-label="close sidebar"
          class="drawer-overlay"
        ></label>
        <nav class="menu min-h-full w-60 bg-base-200 p-4">
          <ul>
            <li>
              <Link href={RouteURL.Login}>{t('app.ui.login')}</Link>
            </li>
            <li>
              <Link href={RouteURL.Register}>{t('app.ui.getStarted')}</Link>
            </li>
          </ul>
        </nav>
      </div>
    </div>
  );
});
