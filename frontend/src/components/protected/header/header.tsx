import { component$, type PropFunction } from '@builder.io/qwik';
import { Link } from '@builder.io/qwik-city';
import { inlineTranslate } from 'qwik-speak';

import { Logo } from '~/components/icons/logo';
import { User } from '~/components/icons/user';
import { RouteURL } from '~/libs/api/route-url';

interface HeaderProps {
  onLogout$: PropFunction<() => Promise<void>>;
}

export const Header = component$<HeaderProps>(props => {
  const t = inlineTranslate();

  return (
    <header>
      <div class="mx-auto max-w-7xl px-3 sm:px-6">
        <nav class="navbar">
          <div class="flex-1">
            <Link href={RouteURL.Dashboard} aria-label="dashboard">
              <Logo height={60} />
            </Link>
          </div>
          <div class="dropdown dropdown-end">
            <div tabIndex={0} role="button" class="btn btn-circle btn-ghost">
              <User />
            </div>
            <ul
              tabIndex={0}
              class="menu dropdown-content z-[1] mt-5 w-40 rounded-box bg-base-100 p-2 shadow"
            >
              <li>
                <Link href={RouteURL.Account}>{t('app.ui.account')}</Link>
              </li>
              <li>
                <button onClick$={props.onLogout$}>{t('app.ui.logout')}</button>
              </li>
            </ul>
          </div>
        </nav>
      </div>
    </header>
  );
});
