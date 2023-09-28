import { $, component$, useSignal } from '@builder.io/qwik';
import {
  type DocumentHead,
  type RequestEvent,
  routeLoader$,
} from '@builder.io/qwik-city';
import { type InitialValues } from '@modular-forms/qwik';
import { Speak, useTranslate } from 'qwik-speak';

import { getClientLogoutRedirection, onProtectedRoute } from '~/services/auth';
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

export const onRequest = async (requestEvent: RequestEvent) => {
  await onProtectedRoute(requestEvent);
};

export const useUpdateAccountFormLoader = routeLoader$<
  InitialValues<UpdateAccountFormSchema>
>(async requestEvent => {
  const {
    me: { fullName },
  } = await getMe(await getServerRequestSender(requestEvent));
  return { fullName };
});

export default component$(() => (
  <Speak
    assets={[
      'account',
      'auth',
      'changePassword',
      'deleteAccount',
      'updateAccount',
      'validation',
    ]}
  >
    <Account />
  </Speak>
));

const Account = component$(() => {
  const t = useTranslate();
  const deleteAccountPending = useSignal(false);
  const updateAccountFormSignal = useUpdateAccountFormLoader();

  const onDeleteAccount = $(async () => {
    deleteAccountPending.value = true;
    await deleteMe(await getClientRequestSender());
    await logout(
      await getClientTokenStorage(),
      await getClientLogoutRedirection(),
    );
    deleteAccountPending.value = false;
  });

  return (
    <>
      <UpdateAccountForm loader={updateAccountFormSignal} />
      <ChangePasswordForm />
      <button onClick$={onDeleteAccount} disabled={deleteAccountPending.value}>
        {t('deleteAccount.deleteAccount')}
      </button>
    </>
  );
});
