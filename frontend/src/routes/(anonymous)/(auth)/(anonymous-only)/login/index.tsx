import { component$ } from '@builder.io/qwik';
import { type DocumentHead, Link } from '@builder.io/qwik-city';
import { inlineTranslate, useSpeak } from 'qwik-speak';

import { RouteURL } from '~/libs/api/route-url';

import { LoginForm } from './login-form';

export const head: DocumentHead = () => {
  const t = inlineTranslate();

  return {
    title: t('head.login.title'),
  };
};

export default component$(() => {
  useSpeak({ assets: ['auth', 'login', 'validation'] });

  return <Login />;
});

const Login = component$(() => {
  const t = inlineTranslate();

  return (
    <>
      <LoginForm />
      <Link href={RouteURL.Register}>{t('login.doNotHaveAccount')}</Link>
      <Link href={RouteURL.RecoverPassword}>{t('login.forgotPassword')}</Link>
    </>
  );
});
