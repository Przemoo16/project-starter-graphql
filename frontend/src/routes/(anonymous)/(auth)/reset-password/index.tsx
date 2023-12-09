import { $, component$ } from '@builder.io/qwik';
import { type DocumentHead, Link, useLocation } from '@builder.io/qwik-city';
import { FormError } from '@modular-forms/qwik';
import { inlineTranslate, useSpeak } from 'qwik-speak';

import {
  ResetPasswordForm,
  type ResetPasswordFormSchema,
} from '~/components/reset-password-form/reset-password-form';
import { hasProblems } from '~/libs/api/has-problems';
import { RouteURL } from '~/libs/api/route-url';
import { getClientRequestSender } from '~/services/requests/get-client-request-sender';
import { resetPassword } from '~/services/user/reset-password';

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
  const loc = useLocation();

  const onSubmit = $(async (password: string) => {
    const t = inlineTranslate();

    const data = await resetPassword(
      getClientRequestSender(),
      loc.url.searchParams.get('token') ?? '',
      password,
    );

    if (hasProblems(data)) {
      throw new FormError<ResetPasswordFormSchema>(
        t('resetPassword.resetPasswordError'),
      );
    }

    return t('resetPassword.resetPasswordSuccess');
  });

  return (
    <>
      <ResetPasswordForm onSubmit={onSubmit} />
      <Link href={RouteURL.Login}>{t('auth.backToLogin')}</Link>
    </>
  );
});
