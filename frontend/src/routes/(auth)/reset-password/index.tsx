import { $, component$ } from '@builder.io/qwik';
import { type DocumentHead, Link, useLocation } from '@builder.io/qwik-city';
import { FormError } from '@modular-forms/qwik';
import { inlineTranslate, useSpeak } from 'qwik-speak';

import { getClientRequestSender } from '~/api/get-client-request-sender';
import {
  ResetPasswordForm,
  type ResetPasswordFormSchema,
} from '~/components/reset-password-form/reset-password-form';
import { hasProblems } from '~/libs/api/has-problems';
import { RouteURL } from '~/libs/api/route-url';
import { type ResetPasswordInput } from '~/services/graphql';
import { resetPassword } from '~/services/user/reset-password';

export const head: DocumentHead = () => {
  const t = inlineTranslate();

  return {
    title: t('app.head.resetPassword.title'),
  };
};

export default component$(() => {
  useSpeak({ assets: ['auth', 'resetPassword', 'validation'] });

  return <ResetPassword />;
});

const ResetPassword = component$(() => {
  const t = inlineTranslate();
  const loc = useLocation();

  const onSubmit = $(async (input: Omit<ResetPasswordInput, 'token'>) => {
    const t = inlineTranslate();

    const data = await resetPassword(getClientRequestSender(), {
      token: loc.url.searchParams.get('token') ?? '',
      ...input,
    });

    if (hasProblems(data)) {
      throw new FormError<ResetPasswordFormSchema>(
        t('resetPassword.resetPasswordError'),
      );
    }
  });

  return (
    <>
      <ResetPasswordForm onSubmit={onSubmit} />
      <Link href={RouteURL.Login}>{t('auth.backToLogin')}</Link>
    </>
  );
});
