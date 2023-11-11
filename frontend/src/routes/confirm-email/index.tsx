import { component$ } from '@builder.io/qwik';
import { type DocumentHead, Link, routeLoader$ } from '@builder.io/qwik-city';
import { Speak, useTranslate } from 'qwik-speak';

import { isProblemPresent } from '~/libs/api/is-problem-present';
import { RouteURL } from '~/libs/api/route-url';
import { getServerRequestSender } from '~/services/requests/get-server-request-sender';
import { confirmEmail } from '~/services/user/confirm-email';

export const head: DocumentHead = {
  title: 'runtime.confirmEmail.head.title',
};

export const useConfirmEmail = routeLoader$(async requestEvent => {
  return await confirmEmail(
    getServerRequestSender(requestEvent),
    requestEvent.url.searchParams.get('token') ?? '',
  );
});

export default component$(() => (
  <Speak assets={['auth', 'confirmEmail']}>
    <ConfirmEmail />
  </Speak>
));

const ConfirmEmail = component$(() => {
  const signal = useConfirmEmail();
  const t = useTranslate();

  const data = signal.value;

  let message = '';
  if ('problems' in data) {
    if (isProblemPresent(data.problems, 'UserEmailAlreadyConfirmedProblem')) {
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
