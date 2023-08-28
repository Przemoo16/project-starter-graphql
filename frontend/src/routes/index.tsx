import { component$ } from '@builder.io/qwik';
import type { DocumentHead } from '@builder.io/qwik-city';

export const head: DocumentHead = {
  title: 'runtime.home.head.title',
};

export default component$(() => <>Home</>);
