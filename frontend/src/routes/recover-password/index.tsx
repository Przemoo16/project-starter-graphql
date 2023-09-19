import { component$ } from '@builder.io/qwik';
import { type DocumentHead, Link } from '@builder.io/qwik-city';
import { Speak, useTranslate } from 'qwik-speak';

import { RecoverPasswordForm } from './recover-password-form';

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

  return (
    <>
      <RecoverPasswordForm />
      <Link href="/login">{t('auth.backToLoginLink')}</Link>
    </>
  );
});
