import { component$ } from '@builder.io/qwik';
import { type DocumentHead, routeLoader$ } from '@builder.io/qwik-city';
import { Speak, useTranslate } from 'qwik-speak';

import { isProblemPresent } from '~/libs/api/errors';
import { confirmEmail } from '~/services/user';

export const head: DocumentHead = {
  title: 'runtime.confirm-email.head.title',
};

export const userConfirmEmail = routeLoader$(async requestEvent => {
  return await confirmEmail(requestEvent.url.searchParams.get('token') ?? '');
});

export default component$(() => (
  <Speak assets={['auth']}>
    <ConfirmEmail />
  </Speak>
));

const ConfirmEmail = component$(() => {
  const signal = userConfirmEmail();
  const t = useTranslate();

  const {
    confirmEmail: { problems },
  } = signal.value;

  let message = '';
  if (problems) {
    if (isProblemPresent(problems, 'UserAlreadyConfirmedProblem')) {
      message = t('auth.userAlreadyConfirmed');
    } else {
      message = t('auth.confirmEmailError');
    }
  } else {
    message = t('auth.confirmEmailSuccess');
  }

  const confirmEmail = t('auth.confirmEmail');

  return (
    <>
      {confirmEmail}
      <div>{message}</div>
    </>
  );
});
