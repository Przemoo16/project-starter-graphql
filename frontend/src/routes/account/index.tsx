import { $, component$, useSignal } from '@builder.io/qwik';
import {
  type DocumentHead,
  type RequestEvent,
  routeLoader$,
  useNavigate,
} from '@builder.io/qwik-city';
import { type InitialValues } from '@modular-forms/qwik';
import { Speak, useTranslate } from 'qwik-speak';

import { RouteURL } from '~/libs/api/urls';
import { onProtectedRoute } from '~/services/auth';
import {
  getClientRequestSender,
  getServerRequestSender,
} from '~/services/requests';
import { getClientTokenStorage } from '~/services/storage';
import { deleteMe, getMe, logout } from '~/services/user';

import { ChangePasswordForm } from './change-password-form';
import {
  UpdateAccountForm,
  type UpdateAccountFormSchema,
} from './update-account-form';

export const head: DocumentHead = {
  title: 'runtime.account.head.title',
};

export const onRequest = async (event: RequestEvent) => {
  await onProtectedRoute(event);
};

export const useUpdateAccountFormLoader = routeLoader$<
  InitialValues<UpdateAccountFormSchema>
>(async ({ cookie }) => {
  const {
    me: { fullName },
  } = await getMe(await getServerRequestSender(cookie));
  return { fullName };
});

export default component$(() => (
  <Speak assets={['account', 'validation']}>
    <Account />
  </Speak>
));

const Account = component$(() => {
  const t = useTranslate();
  const nav = useNavigate();
  const deleteAccountPending = useSignal(false);
  const updateAccountFormSignal = useUpdateAccountFormLoader();

  const onDeleteAccount = $(async () => {
    deleteAccountPending.value = true;
    await deleteMe(await getClientRequestSender());
    await logout(await getClientTokenStorage());
    deleteAccountPending.value = false;
    await nav(RouteURL.Login, { forceReload: true });
  });

  return (
    <>
      <UpdateAccountForm loader={updateAccountFormSignal} />
      <ChangePasswordForm />
      <button onClick$={onDeleteAccount} disabled={deleteAccountPending.value}>
        {t('account.deleteAccount')}
      </button>
    </>
  );
});
