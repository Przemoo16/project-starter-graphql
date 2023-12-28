import { $, component$ } from '@builder.io/qwik';
import { type DocumentHead } from '@builder.io/qwik-city';
import { inlineTranslate, useSpeak } from 'qwik-speak';

import { getClientRequestSender } from '~/api/get-client-request-sender';
import { FormLink } from '~/components/auth/form-link/form-link';
import { FormTitle } from '~/components/auth/form-title/form-title';
import { LinksContainer } from '~/components/auth/links-container/links-container';
import { RecoverPasswordForm } from '~/components/auth/recover-password-form/recover-password-form';
import { RouteURL } from '~/libs/api/route-url';
import { recoverPassword } from '~/services/user/recover-password';

export const head: DocumentHead = () => {
  const t = inlineTranslate();

  return {
    title: t('app.head.recoverPassword.title'),
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
      <FormTitle>{t('recoverPassword.recoverYourPassword')}</FormTitle>
      <RecoverPasswordForm onSubmit={onSubmit} />
      <LinksContainer>
        <FormLink href={RouteURL.Login}>{t('auth.backToLogin')}</FormLink>
      </LinksContainer>
    </>
  );
});
