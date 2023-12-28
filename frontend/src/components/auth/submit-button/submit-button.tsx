import { component$, Slot } from '@builder.io/qwik';

import { LoadingButton } from '~/components/common/loading-button/loading-button';

interface SubmitButtonProps {
  submitting: boolean;
}

export const SubmitButton = component$(({ submitting }: SubmitButtonProps) => (
  <div class="mt-6 flex flex-col">
    <LoadingButton type="submit" loading={submitting}>
      <Slot />
    </LoadingButton>
  </div>
));
