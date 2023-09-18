import { $, component$ } from '@builder.io/qwik';
import { type DocumentHead, useLocation } from '@builder.io/qwik-city';
import { FormError, type SubmitHandler } from '@modular-forms/qwik';
import { inlineTranslate, Speak, useSpeakContext } from 'qwik-speak';

import {
  ResetPasswordForm,
  type ResetPasswordFormSchema,
} from '~/components/forms/reset-password';
import { REQUEST_SENDER } from '~/services/context';
import { resetPassword } from '~/services/user';

export const head: DocumentHead = {
  title: 'runtime.resetPassword.head.title',
};

export default component$(() => (
  <Speak assets={['auth', 'validation']}>
    <ResetPassword />
  </Speak>
));

const ResetPassword = component$(() => {
  const ctx = useSpeakContext();
  const loc = useLocation();

  const handleSubmit = $<SubmitHandler<ResetPasswordFormSchema>>(
    async (values, _event) => {
      const { problems } = await resetPassword(
        REQUEST_SENDER,
        loc.url.searchParams.get('token') ?? '',
        values.password,
      );

      if (problems) {
        throw new FormError<ResetPasswordFormSchema>(
          inlineTranslate('auth.resetPasswordError', ctx),
        );
      }
    },
  );

  return <ResetPasswordForm onSubmit={handleSubmit} />;
});
