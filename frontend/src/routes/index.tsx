import { component$ } from '@builder.io/qwik';
import type { DocumentHead } from '@builder.io/qwik-city';
import { inlineTranslate } from 'qwik-speak';

export const head: DocumentHead = () => {
  const t = inlineTranslate();

  return {
    title: t('head.home.title'),
  };
};

export default component$(() => <>Home</>);
