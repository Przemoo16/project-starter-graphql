import { $, component$ } from '@builder.io/qwik';
import { type DocumentHead, Link } from '@builder.io/qwik-city';
import { type SubmitHandler } from '@modular-forms/qwik';
import { Speak, useTranslate } from 'qwik-speak';

import {
  RecoverPasswordForm,
  type RecoverPasswordFormSchema,
} from '~/components/forms/recover-password';
import { REQUEST_SENDER } from '~/services/context';
import { recoverPassword } from '~/services/user';

export const head: DocumentHead = {
  title: 'runtime.recoverPassword.head.title',
};

export default component$(() => (
  <Speak assets={['auth', 'validation']}>
    <RecoverPassword />
  </Speak>
));

const RecoverPassword = component$(() => {
  const t = useTranslate();
  const handleSubmit = $<SubmitHandler<RecoverPasswordFormSchema>>(
    async (values, _event) => {
      await recoverPassword(REQUEST_SENDER, values.email);
    },
  );

  return (
    <>
      <RecoverPasswordForm onSubmit={handleSubmit} />
      <Link href="/login">{t('auth.backToLoginLink')}</Link>
    </>
  );
});
