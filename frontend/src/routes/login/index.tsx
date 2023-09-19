import { component$ } from '@builder.io/qwik';
import { type DocumentHead, Link } from '@builder.io/qwik-city';
import { Speak, useTranslate } from 'qwik-speak';

import { LoginForm } from './login-form';

export const head: DocumentHead = {
  title: 'runtime.login.head.title',
};

export default component$(() => (
  <Speak assets={['auth', 'validation']}>
    <Login />
  </Speak>
));

const Login = component$(() => {
  const t = useTranslate();

  return (
    <>
      <LoginForm />
      <Link href="/register">{t('auth.registerLink')}</Link>
      <Link href="/recover-password">{t('auth.recoverPasswordLink')}</Link>
    </>
  );
});
