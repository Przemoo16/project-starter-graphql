import { component$ } from '@builder.io/qwik';
import type { DocumentHead } from '@builder.io/qwik-city';

export const head: DocumentHead = {
  title: 'runtime.404.head.title',
};

// FIXME: The custom 404 page doesn't work: https://github.com/BuilderIO/qwik/issues/5030
export default component$(() => <>Not found</>);
