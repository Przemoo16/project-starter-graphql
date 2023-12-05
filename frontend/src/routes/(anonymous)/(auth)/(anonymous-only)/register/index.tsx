import { component$ } from '@builder.io/qwik';
import { type DocumentHead, Link } from '@builder.io/qwik-city';
import { inlineTranslate, useSpeak } from 'qwik-speak';

import { RouteURL } from '~/libs/api/route-url';

import { RegisterForm } from './register-form';

export const head: DocumentHead = () => {
  const t = inlineTranslate();

  return {
    title: t('head.register.title'),
  };
};

export default component$(() => {
  useSpeak({ assets: ['account', 'auth', 'register', 'validation'] });

  return <Register />;
});

const Register = component$(() => {
  const t = inlineTranslate();

  return (
    <>
      <RegisterForm />
      <Link href={RouteURL.Login}>{t('register.doHaveAccount')}</Link>
    </>
  );
});
