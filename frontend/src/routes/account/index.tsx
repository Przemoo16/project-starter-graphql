import { $, component$, useSignal } from '@builder.io/qwik';
import {
  type DocumentHead,
  routeLoader$,
  useNavigate,
} from '@builder.io/qwik-city';
import { type InitialValues } from '@modular-forms/qwik';
import { Speak, useTranslate } from 'qwik-speak';

import { getClientRequestSender } from '~/services/requests';
import { getClientTokenStorage } from '~/services/storage';
import { deleteMe, logout } from '~/services/user';

import { ChangePasswordForm } from './change-password-form';
import {
  UpdateAccountForm,
  type UpdateAccountFormSchema,
} from './update-account-form';

export const head: DocumentHead = {
  title: 'runtime.account.head.title',
};

export const useUpdateAccountFormLoader = routeLoader$<
  InitialValues<UpdateAccountFormSchema>
>(() => ({
  fullName: '', // TODO: Fill details from the user
}));

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
    await nav('/login', { forceReload: true });
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
