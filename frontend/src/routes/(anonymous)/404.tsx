import { component$ } from '@builder.io/qwik';
import { type DocumentHead } from '@builder.io/qwik-city';
import { inlineTranslate, useSpeak } from 'qwik-speak';

export const head: DocumentHead = () => {
  const t = inlineTranslate();

  return {
    title: t('app.head.notFound.title'),
  };
};

export default component$(() => {
  useSpeak({ assets: ['notFound'] });

  return <NotFound />;
});

const NotFound = component$(() => {
  const t = inlineTranslate();

  return <>{t('notFound.pageNotFound')}</>;
});
