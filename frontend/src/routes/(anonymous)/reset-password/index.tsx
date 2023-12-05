import { component$ } from '@builder.io/qwik';
import { type DocumentHead, Link } from '@builder.io/qwik-city';
import { inlineTranslate, useSpeak } from 'qwik-speak';

import { RouteURL } from '~/libs/api/route-url';

import { ResetPasswordForm } from './reset-password-form';

export const head: DocumentHead = () => {
  const t = inlineTranslate();

  return {
    title: t('head.resetPassword.title'),
  };
};

export default component$(() => {
  useSpeak({ assets: ['auth', 'resetPassword', 'validation'] });

  return <ResetPassword />;
});

const ResetPassword = component$(() => {
  const t = inlineTranslate();

  return (
    <>
      <ResetPasswordForm />
      <Link href={RouteURL.Login}>{t('auth.backToLogin')}</Link>
    </>
  );
});
