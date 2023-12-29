import { component$ } from '@builder.io/qwik';
import { type DocumentHead, Link } from '@builder.io/qwik-city';
import { inlineTranslate, useSpeak } from 'qwik-speak';

import { RouteURL } from '~/libs/api/route-url';

export const head: DocumentHead = () => {
  const t = inlineTranslate();

  return {
    title: t('app.head.notFound.title'),
    meta: [
      {
        name: 'description',
        content: t('app.head.notFound.description'),
      },
    ],
  };
};

export default component$(() => {
  useSpeak({ assets: ['notFound'] });

  return <NotFound />;
});

const NotFound = component$(() => {
  const t = inlineTranslate();

  return (
    <div class="grid h-full place-items-center">
      <div class="p-4 text-center">
        <h1 class="text-8xl font-bold">{t('notFound.404')}</h1>
        <p class="mt-6">{t('notFound.pageDoesNotExist')}</p>
        <Link href={RouteURL.Home} class="btn btn-primary mt-6">
          {t('notFound.backToHome')}
        </Link>
      </div>
    </div>
  );
});
