import { $, component$ } from '@builder.io/qwik';
import { type DocumentHead, Link } from '@builder.io/qwik-city';
import { inlineTranslate, useSpeak } from 'qwik-speak';

import { getClientRequestSender } from '~/api/get-client-request-sender';
import { RecoverPasswordForm } from '~/components/recover-password-form/recover-password-form';
import { RouteURL } from '~/libs/api/route-url';
import { recoverPassword } from '~/services/user/recover-password';

export const head: DocumentHead = () => {
  const t = inlineTranslate();

  return {
    title: t('head.recoverPassword.title'),
  };
};

export default component$(() => {
  useSpeak({ assets: ['auth', 'recoverPassword', 'validation'] });

  return <RecoverPassword />;
});

const RecoverPassword = component$(() => {
  const t = inlineTranslate();

  const onSubmit = $(async (email: string) => {
    const t = inlineTranslate();
    await recoverPassword(getClientRequestSender(), email);
    return t('recoverPassword.recoverPasswordSuccess');
  });

  return (
    <>
      <RecoverPasswordForm onSubmit={onSubmit} />
      <Link href={RouteURL.Login}>{t('auth.backToLogin')}</Link>
    </>
  );
});
