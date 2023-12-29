import { $, component$ } from '@builder.io/qwik';
import { type DocumentHead, useLocation } from '@builder.io/qwik-city';
import { FormError } from '@modular-forms/qwik';
import { inlineTranslate, useSpeak } from 'qwik-speak';

import { getClientRequestSender } from '~/api/get-client-request-sender';
import { Link } from '~/components/auth/link/link';
import {
  ResetPasswordForm,
  type ResetPasswordFormSchema,
} from '~/components/auth/reset-password-form/reset-password-form';
import { Title } from '~/components/auth/title/title';
import { hasProblems } from '~/libs/api/has-problems';
import { RouteURL } from '~/libs/api/route-url';
import { type ResetPasswordInput } from '~/services/graphql';
import { resetPassword } from '~/services/user/reset-password';

export const head: DocumentHead = () => {
  const t = inlineTranslate();

  return {
    title: t('app.head.resetPassword.title'),
    meta: [
      {
        name: 'description',
        content: t('app.head.resetPassword.description'),
      },
      {
        name: 'robots',
        content: 'noindex',
      },
    ],
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
      <Title>{t('resetPassword.resetYourPassword')}</Title>
      <ResetPasswordForm onSubmit={onSubmit} />
      <Link href={RouteURL.Login}>{t('auth.backToLogin')}</Link>
    </>
  );
});
