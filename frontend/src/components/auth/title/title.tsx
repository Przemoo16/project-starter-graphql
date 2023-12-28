import { component$, Slot } from '@builder.io/qwik';

export const Title = component$(() => (
  <h1 class="text-center text-2xl font-bold">
    <Slot />
  </h1>
));
