import { $, component$, useSignal } from '@builder.io/qwik';
import {
  type DocumentHead,
  routeLoader$,
  useNavigate,
} from '@builder.io/qwik-city';
import { type InitialValues } from '@modular-forms/qwik';
import { Speak, useTranslate } from 'qwik-speak';

import { getTokenStorage, REQUEST_SENDER } from '~/services/context';
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
    await deleteMe(REQUEST_SENDER);
    await logout(await getTokenStorage());
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
