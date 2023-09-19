import { component$ } from '@builder.io/qwik';
import { type DocumentHead, Link } from '@builder.io/qwik-city';
import { Speak, useTranslate } from 'qwik-speak';

import { RegisterForm } from './register-form';

export const head: DocumentHead = {
  title: 'runtime.register.head.title',
};

export default component$(() => (
  <Speak assets={['account', 'auth', 'validation']}>
    <Register />
  </Speak>
));

const Register = component$(() => {
  const t = useTranslate();

  return (
    <>
      <RegisterForm />
      <Link href="/login">{t('auth.loginLink')}</Link>
    </>
  );
});
