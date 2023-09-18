import { $, component$, useSignal } from '@builder.io/qwik';
import {
  type DocumentHead,
  routeLoader$,
  useNavigate,
} from '@builder.io/qwik-city';
import {
  FormError,
  type InitialValues,
  type SubmitHandler,
} from '@modular-forms/qwik';
import {
  inlineTranslate,
  Speak,
  useSpeakContext,
  useTranslate,
} from 'qwik-speak';

import {
  ChangePasswordForm,
  type ChangePasswordFormSchema,
} from '~/components/forms/change-password';
import {
  UpdateAccountForm,
  type UpdateAccountFormSchema,
} from '~/components/forms/update-account';
import { isProblemPresent } from '~/libs/api/errors';
import { getTokenStorage, REQUEST_SENDER } from '~/services/context';
import { changeMyPassword, deleteMe, logout, updateMe } from '~/services/user';

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
  const ctx = useSpeakContext();
  const nav = useNavigate();
  const deleteAccountPending = useSignal(false);
  const updateAccountFormSignal = useUpdateAccountFormLoader();

  const handleUpdateAccountSubmit = $<SubmitHandler<UpdateAccountFormSchema>>(
    async (values, _event) => {
      const { problems } = await updateMe(REQUEST_SENDER, values.fullName);

      if (problems) {
        throw new FormError<UpdateAccountFormSchema>(
          inlineTranslate('account.updateAccountError', ctx),
        );
      }
    },
  );

  const handleChangePasswordSubmit = $<SubmitHandler<ChangePasswordFormSchema>>(
    async (values, _event) => {
      const { problems } = await changeMyPassword(
        REQUEST_SENDER,
        values.currentPassword,
        values.newPassword,
      );

      if (problems) {
        let error = '';
        if (isProblemPresent(problems, 'InvalidPasswordProblem')) {
          error = inlineTranslate('account.invalidCurrentPassword', ctx);
        } else {
          error = inlineTranslate('account.changePasswordError', ctx);
        }
        throw new FormError<ChangePasswordFormSchema>(error);
      }
    },
  );

  const onDeleteAccount = $(async () => {
    deleteAccountPending.value = true;
    await deleteMe(REQUEST_SENDER);
    await logout(await getTokenStorage());
    deleteAccountPending.value = false;
    await nav('/login', { forceReload: true });
  });

  return (
    <>
      <UpdateAccountForm
        onSubmit={handleUpdateAccountSubmit}
        loader={updateAccountFormSignal}
      />
      <ChangePasswordForm onSubmit={handleChangePasswordSubmit} />
      <button onClick$={onDeleteAccount} disabled={deleteAccountPending.value}>
        {t('account.deleteAccount')}
      </button>
    </>
  );
});
