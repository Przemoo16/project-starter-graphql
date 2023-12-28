import { component$, Slot } from '@builder.io/qwik';

export const FormBody = component$(() => (
  <div class="flex flex-col gap-2">
    <Slot />
  </div>
));
