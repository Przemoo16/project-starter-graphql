import { $, component$ } from '@builder.io/qwik';
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
} from '~/components/protected/change-password-form/change-password-form';
import { DeleteAccountModal } from '~/components/protected/delete-account-modal/delete-account-modal';
import { SettingsSection } from '~/components/protected/settings-section/settings-section';
import {
  UpdateAccountForm,
  type UpdateAccountFormSchema,
} from '~/components/protected/update-account-form/update-account-form';
import { hasProblems } from '~/libs/api/has-problems';
import { isProblemPresent } from '~/libs/api/is-problem-present';
import {
  type ChangeMyPasswordInput,
  type UpdateMeInput,
} from '~/services/graphql';
import { changeMyPassword } from '~/services/user/change-my-password';
import { deleteMe } from '~/services/user/delete-me';
import { getMe } from '~/services/user/get-me';
import { logout } from '~/services/user/logout';
import { updateMe } from '~/services/user/update-me';

export const head: DocumentHead = () => {
  const t = inlineTranslate();

  return {
    title: t('app.head.account.title'),
    meta: [
      {
        name: 'description',
        content: t('app.head.account.description'),
      },
    ],
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
    assets: ['account', 'auth', 'validation'],
  });

  return <Account />;
});

const Account = component$(() => {
  const t = inlineTranslate();
  const updateAccountFormSignal = useUpdateAccountFormLoader();

  const onChangePassword = $(async (input: ChangeMyPasswordInput) => {
    const t = inlineTranslate();

    const data = await changeMyPassword(getClientRequestSender(), input);

    if (hasProblems(data)) {
      let error = '';
      if (isProblemPresent(data.problems, 'InvalidPasswordProblem')) {
        error = t('account.invalidCurrentPassword');
      } else {
        error = t('account.changePasswordError');
      }
      throw new FormError<ChangePasswordFormSchema>(error);
    }
  });

  const onUpdateAccount = $(async (input: UpdateMeInput) => {
    const t = inlineTranslate();

    const data = await updateMe(getClientRequestSender(), input);

    if (hasProblems(data)) {
      throw new FormError<UpdateAccountFormSchema>(
        t('account.updateAccountError'),
      );
    }

    return data;
  });

  const onDeleteAccount = $(async () => {
    await deleteMe(getClientRequestSender());
    logout(getClientTokenStorage(), getClientLogoutRedirection());
  });

  return (
    <div class="my-6 flex flex-col items-center justify-center gap-5">
      <SettingsSection title={t('account.updateYourAccount')}>
        <UpdateAccountForm
          loader={updateAccountFormSignal}
          onSubmit$={onUpdateAccount}
        />
      </SettingsSection>
      <SettingsSection title={t('account.changeYourPassword')}>
        <ChangePasswordForm onSubmit$={onChangePassword} />
      </SettingsSection>
      <SettingsSection title={t('account.deleteYourAccount')}>
        <p>{t('account.deleteAccountDescription')}</p>
        <DeleteAccountModal onDelete$={onDeleteAccount} />
      </SettingsSection>
    </div>
  );
});
