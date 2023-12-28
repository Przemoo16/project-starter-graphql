import { component$ } from '@builder.io/qwik';
import { type DocumentHead, Link, routeLoader$ } from '@builder.io/qwik-city';
import { inlineTranslate, useSpeak } from 'qwik-speak';

import { getServerRequestSender } from '~/api/get-server-request-sender';
import { hasProblems } from '~/libs/api/has-problems';
import { isProblemPresent } from '~/libs/api/is-problem-present';
import { RouteURL } from '~/libs/api/route-url';
import { confirmEmail } from '~/services/user/confirm-email';

export const head: DocumentHead = () => {
  const t = inlineTranslate();

  return {
    title: t('app.head.confirmEmail.title'),
  };
};

export const useConfirmEmail = routeLoader$(async requestEvent => {
  return await confirmEmail(
    getServerRequestSender(requestEvent),
    requestEvent.url.searchParams.get('token') ?? '',
  );
});

export default component$(() => {
  useSpeak({ assets: ['auth', 'confirmEmail'] });

  return <ConfirmEmail />;
});

const ConfirmEmail = component$(() => {
  const signal = useConfirmEmail();
  const t = inlineTranslate();

  const data = signal.value;

  let message = '';
  if (hasProblems(data)) {
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
      <h1 class="text-center text-2xl font-bold">
        {t('confirmEmail.confirmEmail')}
      </h1>
      <div>{message}</div>
      <Link href={RouteURL.Login} class="btn btn-primary mt-5">
        {t('auth.backToLogin')}
      </Link>
    </>
  );
});
