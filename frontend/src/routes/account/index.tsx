import { $, component$, useSignal } from '@builder.io/qwik';
import {
  type DocumentHead,
  type RequestHandler,
  routeLoader$,
} from '@builder.io/qwik-city';
import { type InitialValues } from '@modular-forms/qwik';
import { inlineTranslate, useSpeak } from 'qwik-speak';

import { getClientLogoutRedirection } from '~/services/auth/get-client-logout-redirection';
import { onProtectedRoute } from '~/services/auth/on-protected-route';
import { getClientRequestSender } from '~/services/requests/get-client-request-sender';
import { getServerRequestSender } from '~/services/requests/get-server-request-sender';
import { getClientTokenStorage } from '~/services/tokens/get-client-token-storage';
import { getServerTokenStorage } from '~/services/tokens/get-server-token-storage';
import { deleteMe } from '~/services/user/delete-me';
import { getMe } from '~/services/user/get-me';
import { logout } from '~/services/user/logout';

import { ChangePasswordForm } from './change-password-form';
import {
  UpdateAccountForm,
  type UpdateAccountFormSchema,
} from './update-account-form';

export const head: DocumentHead = () => {
  const t = inlineTranslate();

  return {
    title: t('head.account.title'),
  };
};

export const onRequest: RequestHandler = requestEvent => {
  onProtectedRoute(requestEvent);
};

export const useUpdateAccountFormLoader = routeLoader$<
  InitialValues<UpdateAccountFormSchema>
>(async requestEvent => {
  return await getMe(
    getServerRequestSender(requestEvent),
    getServerTokenStorage(requestEvent.cookie),
  );
});

export default component$(() => {
  useSpeak({
    assets: [
      'account',
      'auth',
      'changePassword',
      'deleteAccount',
      'updateAccount',
      'validation',
    ],
  });

  return <Account />;
});

const Account = component$(() => {
  const t = inlineTranslate();
  const deleteAccountPending = useSignal(false);
  const updateAccountFormSignal = useUpdateAccountFormLoader();

  const onDeleteAccount = $(async () => {
    deleteAccountPending.value = true;
    await deleteMe(getClientRequestSender());
    logout(getClientTokenStorage(), getClientLogoutRedirection());
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
