import { component$ } from '@builder.io/qwik';
import {
  type DocumentHead,
  Link,
  type RequestHandler,
} from '@builder.io/qwik-city';
import { inlineTranslate, useSpeak } from 'qwik-speak';

import { RouteURL } from '~/libs/api/route-url';
import { onOnlyAnonymousRoute } from '~/services/auth/on-only-anonymous-route';

import { LoginForm } from './login-form';

export const head: DocumentHead = () => {
  const t = inlineTranslate();

  return {
    title: t('head.login.title'),
  };
};

export const onRequest: RequestHandler = requestEvent => {
  onOnlyAnonymousRoute(requestEvent);
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
