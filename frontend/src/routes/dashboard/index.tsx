import { component$ } from '@builder.io/qwik';
import type { DocumentHead } from '@builder.io/qwik-city';

export const head: DocumentHead = {
  title: 'runtime.dashboard.head.title',
};

export default component$(() => <>Dashboard</>);
