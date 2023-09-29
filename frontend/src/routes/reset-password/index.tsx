import { component$ } from '@builder.io/qwik';
import { type DocumentHead, Link } from '@builder.io/qwik-city';
import { Speak, useTranslate } from 'qwik-speak';

import { RouteURL } from '~/libs/api/route-url';

import { ResetPasswordForm } from './reset-password-form';

export const head: DocumentHead = {
  title: 'runtime.resetPassword.head.title',
};

export default component$(() => (
  <Speak assets={['auth', 'resetPassword', 'validation']}>
    <ResetPassword />
  </Speak>
));

const ResetPassword = component$(() => {
  const t = useTranslate();

  return (
    <>
      <ResetPasswordForm />
      <Link href={RouteURL.Login}>{t('auth.backToLogin')}</Link>
    </>
  );
});
