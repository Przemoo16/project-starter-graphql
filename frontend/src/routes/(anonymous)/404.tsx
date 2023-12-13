import { component$ } from '@builder.io/qwik';
import type { DocumentHead } from '@builder.io/qwik-city';
import { inlineTranslate } from 'qwik-speak';

export const head: DocumentHead = () => {
  const t = inlineTranslate();

  return {
    title: t('head.404.title'),
  };
};

export default component$(() => <>Not found</>);
