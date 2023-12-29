import { $, component$ } from '@builder.io/qwik';
import { type DocumentHead } from '@builder.io/qwik-city';
import { inlineTranslate, useSpeak } from 'qwik-speak';

import { getClientRequestSender } from '~/api/get-client-request-sender';
import { Link } from '~/components/auth/link/link';
import { RecoverPasswordForm } from '~/components/auth/recover-password-form/recover-password-form';
import { Title } from '~/components/auth/title/title';
import { RouteURL } from '~/libs/api/route-url';
import { recoverPassword } from '~/services/user/recover-password';

export const head: DocumentHead = () => {
  const t = inlineTranslate();

  return {
    title: t('app.head.recoverPassword.title'),
    meta: [
      {
        name: 'description',
        content: t('app.head.recoverPassword.description'),
      },
    ],
  };
};

export default component$(() => {
  useSpeak({ assets: ['auth', 'recoverPassword', 'validation'] });

  return <RecoverPassword />;
});

const RecoverPassword = component$(() => {
  const t = inlineTranslate();

  const onSubmit = $(async (email: string) => {
    await recoverPassword(getClientRequestSender(), email);
  });

  return (
    <>
      <Title>{t('recoverPassword.recoverYourPassword')}</Title>
      <RecoverPasswordForm onSubmit={onSubmit} />
      <Link href={RouteURL.Login}>{t('auth.backToLogin')}</Link>
    </>
  );
});
