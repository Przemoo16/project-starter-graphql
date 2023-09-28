import { component$ } from '@builder.io/qwik';
import { type DocumentHead, Link, routeLoader$ } from '@builder.io/qwik-city';
import { Speak, useTranslate } from 'qwik-speak';

import { isProblemPresent } from '~/libs/api/errors';
import { RouteURL } from '~/libs/api/urls';
import { getServerRequestSender } from '~/services/requests';
import { confirmEmail } from '~/services/user';

export const head: DocumentHead = {
  title: 'runtime.confirmEmail.head.title',
};

export const useConfirmEmail = routeLoader$(
  async requestEvent =>
    await confirmEmail(
      await getServerRequestSender(requestEvent),
      requestEvent.url.searchParams.get('token') ?? '',
    ),
);

export default component$(() => (
  <Speak assets={['auth', 'confirmEmail']}>
    <ConfirmEmail />
  </Speak>
));

const ConfirmEmail = component$(() => {
  const signal = useConfirmEmail();
  const t = useTranslate();

  const { problems } = signal.value;

  let message = '';
  if (problems) {
    if (isProblemPresent(problems, 'UserEmailAlreadyConfirmedProblem')) {
      message = t('confirmEmail.emailAlreadyConfirmed');
    } else {
      message = t('confirmEmail.confirmEmailError');
    }
  } else {
    message = t('confirmEmail.confirmEmailSuccess');
  }

  return (
    <>
      {t('confirmEmail.confirmEmail')}
      <div>{message}</div>
      <Link href={RouteURL.Login}>{t('auth.backToLogin')}</Link>
    </>
  );
});
