import { component$ } from '@builder.io/qwik';
import {
  type DocumentHead,
  Link,
  type RequestHandler,
} from '@builder.io/qwik-city';
import { Speak, useTranslate } from 'qwik-speak';

import { RouteURL } from '~/libs/api/route-url';
import { onOnlyAnonymousRoute } from '~/services/auth/on-only-anonymous-route';

import { LoginForm } from './login-form';

export const head: DocumentHead = {
  title: 'runtime.login.head.title',
};

export const onRequest: RequestHandler = requestEvent => {
  onOnlyAnonymousRoute(requestEvent);
};

export default component$(() => (
  <Speak assets={['auth', 'login', 'validation']}>
    <Login />
  </Speak>
));

const Login = component$(() => {
  const t = useTranslate();

  return (
    <>
      <LoginForm />
      <Link href={RouteURL.Register}>{t('login.doNotHaveAccount')}</Link>
      <Link href={RouteURL.RecoverPassword}>{t('login.forgotPassword')}</Link>
    </>
  );
});
