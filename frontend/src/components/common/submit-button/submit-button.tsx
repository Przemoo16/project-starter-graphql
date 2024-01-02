import { component$, Slot } from '@builder.io/qwik';

import { LoadingButton } from '~/components/common/loading-button/loading-button';

interface SubmitButtonProps {
  submitting: boolean;
}

export const SubmitButton = component$<SubmitButtonProps>(({ submitting }) => (
  <LoadingButton
    type="submit"
    additionalClass="btn-primary"
    loading={submitting}
  >
    <Slot />
  </LoadingButton>
));
