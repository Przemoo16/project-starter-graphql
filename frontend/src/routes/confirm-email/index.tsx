import { component$ } from '@builder.io/qwik';
import { type DocumentHead, routeLoader$ } from '@builder.io/qwik-city';
import { Speak, useTranslate } from 'qwik-speak';

import { isProblemPresent } from '~/libs/api/errors';
import { REQUEST_SENDER } from '~/services/context';
import { confirmEmail } from '~/services/user';

export const head: DocumentHead = {
  title: 'runtime.confirm-email.head.title',
};

export const useConfirmEmail = routeLoader$(async requestEvent => {
  return await confirmEmail(
    REQUEST_SENDER,
    requestEvent.url.searchParams.get('token') ?? '',
  );
});

export default component$(() => (
  <Speak assets={['auth']}>
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
      message = t('auth.accountEmailAlreadyConfirmed');
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
