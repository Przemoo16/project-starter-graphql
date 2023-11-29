import { component$ } from '@builder.io/qwik';
import {
  type DocumentHead,
  Link,
  type RequestHandler,
} from '@builder.io/qwik-city';
import { inlineTranslate, useSpeak } from 'qwik-speak';

import { RouteURL } from '~/libs/api/route-url';
import { onOnlyAnonymousRoute } from '~/services/auth/on-only-anonymous-route';

import { RegisterForm } from './register-form';

export const head: DocumentHead = () => {
  const t = inlineTranslate();

  return {
    title: t('head.register.title'),
  };
};

export const onRequest: RequestHandler = requestEvent => {
  onOnlyAnonymousRoute(requestEvent);
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
