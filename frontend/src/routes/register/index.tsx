import { component$ } from '@builder.io/qwik';
import type { DocumentHead } from '@builder.io/qwik-city';

export const head: DocumentHead = {
  title: 'runtime.register.head.title',
};

export default component$(() => <>Register</>);
