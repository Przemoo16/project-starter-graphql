import { component$, Slot } from '@builder.io/qwik';

export const LinksContainer = component$(() => (
  <div class="mt-5 flex flex-col items-center justify-center gap-1">
    <Slot />
  </div>
));
