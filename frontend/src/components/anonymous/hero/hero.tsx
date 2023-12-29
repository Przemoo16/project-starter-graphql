import { component$ } from '@builder.io/qwik';
import { Link } from '@builder.io/qwik-city';
import { inlineTranslate } from 'qwik-speak';

import { RouteURL } from '~/libs/api/route-url';

export const Hero = component$(() => {
  const t = inlineTranslate();

  return (
    <div class="hero h-full bg-base-200">
      <div class="hero-content text-center">
        <div class="max-w-md">
          <h1 class="text-5xl font-bold">{t('home.helloThere')}</h1>
          <p class="mt-6">{t('home.hero')}</p>
          <Link href={RouteURL.Register} class="btn btn-primary mt-6">
            {t('app.ui.getStarted')}
          </Link>
        </div>
      </div>
    </div>
  );
});
