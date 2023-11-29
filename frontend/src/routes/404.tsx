import { component$ } from '@builder.io/qwik';
import type { DocumentHead } from '@builder.io/qwik-city';
import { inlineTranslate } from 'qwik-speak';

export const head: DocumentHead = () => {
  const t = inlineTranslate();

  return {
    title: t('head.404.title'),
  };
};

// FIXME: The custom 404 page doesn't work: https://github.com/BuilderIO/qwik/issues/5030
export default component$(() => <>Not found</>);
