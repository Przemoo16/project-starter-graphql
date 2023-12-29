import { component$ } from '@builder.io/qwik';
import { type DocumentHead } from '@builder.io/qwik-city';
import { inlineTranslate, useSpeak } from 'qwik-speak';

import { Hero } from '~/components/anonymous/hero/hero';

export const head: DocumentHead = () => {
  const t = inlineTranslate();

  return {
    title: t('app.head.home.title'),
    meta: [
      {
        name: 'description',
        content: t('app.head.home.description'),
      },
    ],
  };
};

export default component$(() => {
  useSpeak({ assets: ['home'] });

  return <Home />;
});

const Home = component$(() => <Hero />);
