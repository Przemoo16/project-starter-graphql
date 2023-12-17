import { $, component$, useSignal } from '@builder.io/qwik';
import { type DocumentHead, routeLoader$ } from '@builder.io/qwik-city';
import { FormError, type InitialValues } from '@modular-forms/qwik';
import { inlineTranslate, useSpeak } from 'qwik-speak';

import { getClientRequestSender } from '~/api/get-client-request-sender';
import { getServerRequestSender } from '~/api/get-server-request-sender';
import { getClientLogoutRedirection } from '~/auth/get-client-logout-redirection';
import { getClientTokenStorage } from '~/auth/get-client-token-storage';
import { getServerTokenStorage } from '~/auth/get-server-token-storage';
import {
  ChangePasswordForm,
  type ChangePasswordFormSchema,
} from '~/components/change-password-form/change-password-form';
import {
  UpdateAccountForm,
  type UpdateAccountFormSchema,
} from '~/components/update-account-form/update-account-form';
import { hasProblems } from '~/libs/api/has-problems';
import { isProblemPresent } from '~/libs/api/is-problem-present';
import { changeMyPassword } from '~/services/user/change-my-password';
import { deleteMe } from '~/services/user/delete-me';
import { getMe } from '~/services/user/get-me';
import { logout } from '~/services/user/logout';
import { updateMe } from '~/services/user/update-me';

export const head: DocumentHead = () => {
  const t = inlineTranslate();

  return {
    title: t('head.account.title'),
  };
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

  const onChangePassword = $(
    async (currentPassword: string, newPassword: string) => {
      const t = inlineTranslate();

      const data = await changeMyPassword(
        getClientRequestSender(),
        currentPassword,
        newPassword,
      );

      if (hasProblems(data)) {
        let error = '';
        if (isProblemPresent(data.problems, 'InvalidPasswordProblem')) {
          error = t('changePassword.invalidCurrentPassword');
        } else {
          error = t('changePassword.changePasswordError');
        }
        throw new FormError<ChangePasswordFormSchema>(error);
      }

      return t('changePassword.changePasswordSuccess');
    },
  );

  const onUpdateAccount = $(async (fullName: string) => {
    const t = inlineTranslate();

    const data = await updateMe(getClientRequestSender(), fullName);

    if (hasProblems(data)) {
      throw new FormError<UpdateAccountFormSchema>(
        t('updateAccount.updateAccountError'),
      );
    }

    return t('updateAccount.updateAccountSuccess');
  });

  const onDeleteAccount = $(async () => {
    deleteAccountPending.value = true;
    await deleteMe(getClientRequestSender());
    logout(getClientTokenStorage(), getClientLogoutRedirection());
    deleteAccountPending.value = false;
  });

  return (
    <>
      <UpdateAccountForm
        loader={updateAccountFormSignal}
        onSubmit={onUpdateAccount}
      />
      <ChangePasswordForm onSubmit={onChangePassword} />
      <button onClick$={onDeleteAccount} disabled={deleteAccountPending.value}>
        {t('deleteAccount.deleteAccount')}
      </button>
    </>
  );
});
