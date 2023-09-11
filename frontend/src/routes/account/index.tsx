import { $, component$ } from '@builder.io/qwik';
import { type DocumentHead, routeLoader$ } from '@builder.io/qwik-city';
import {
  custom$,
  FormError,
  getValue,
  type InitialValues,
  maxLength,
  minLength,
  required,
  reset,
  setResponse,
  type SubmitHandler,
  useForm,
} from '@modular-forms/qwik';
import {
  inlineTranslate,
  Speak,
  useSpeakContext,
  useTranslate,
} from 'qwik-speak';

import { TextInput } from '~/components/text-input/text-input';
import { MAX_FULL_NAME_LENGTH, MIN_PASSWORD_LENGTH } from '~/constants';
import { isProblemPresent } from '~/libs/api/errors';
import { changePassword, updateAccount } from '~/services/user';

export const head: DocumentHead = {
  title: 'runtime.account.head.title',
};

type UpdateAccountForm = {
  fullName: string;
};

type ChangePasswordForm = {
  currentPassword: string;
  newPassword: string;
  repeatNewPassword: string;
};

export const useUpdateAccountFormLoader = routeLoader$<
  InitialValues<UpdateAccountForm>
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
  const [updateAccountForm, UpdateAccount] = useForm<UpdateAccountForm>({
    loader: useUpdateAccountFormLoader(),
  });
  const [changePasswordForm, ChangePassword] = useForm<ChangePasswordForm>({
    loader: {
      value: { currentPassword: '', newPassword: '', repeatNewPassword: '' },
    },
  });

  const handleUpdateAccountSubmit = $<SubmitHandler<UpdateAccountForm>>(
    async (values, _event) => {
      const {
        updateMe: { problems },
      } = await updateAccount(values.fullName);

      if (problems) {
        throw new FormError<UpdateAccountForm>(
          inlineTranslate('account.updateAccountError', ctx),
        );
      }

      setResponse(changePasswordForm, {
        message: inlineTranslate('account.updateAccountSuccess', ctx),
      });
      reset(changePasswordForm);
    },
  );

  const handleChangePasswordSubmit = $<SubmitHandler<ChangePasswordForm>>(
    async (values, _event) => {
      const {
        changeMyPassword: { problems },
      } = await changePassword(values.currentPassword, values.newPassword);

      if (problems) {
        let error = '';
        if (isProblemPresent(problems, 'InvalidPasswordProblem')) {
          error = inlineTranslate('account.invalidCurrentPassword', ctx);
        } else {
          error = inlineTranslate('account.changePasswordError', ctx);
        }
        throw new FormError<UpdateAccountForm>(error);
      }

      setResponse(changePasswordForm, {
        message: inlineTranslate('account.changePasswordSuccess', ctx),
      });
    },
  );

  const fullNameLabel = t('account.fullName');

  const currentPasswordLabel = t('account.currentPassword');
  const newPasswordLabel = t('account.newPassword');
  const repeatNewPasswordLabel = t('account.repeatNewPassword');

  return (
    <>
      <UpdateAccount.Form onSubmit$={handleUpdateAccountSubmit} shouldDirty>
        <UpdateAccount.Field
          name="fullName"
          validate={[
            required(t('validation.required')),
            maxLength(
              MAX_FULL_NAME_LENGTH,
              t('validation.maxFullName', { max: MAX_FULL_NAME_LENGTH }),
            ),
          ]}
        >
          {(field, props) => (
            <TextInput
              {...props}
              type="text"
              label={fullNameLabel}
              placeholder="Jon Doe"
              value={field.value}
              error={field.error}
              required
            />
          )}
        </UpdateAccount.Field>
        <div>{updateAccountForm.response.message}</div>
        <button type="submit" disabled={updateAccountForm.submitting}>
          {t('account.updateAccount')}
        </button>
      </UpdateAccount.Form>
      <ChangePassword.Form onSubmit$={handleChangePasswordSubmit}>
        <ChangePassword.Field
          name="currentPassword"
          validate={[required(t('validation.required'))]}
        >
          {(field, props) => (
            <TextInput
              {...props}
              type="password"
              label={currentPasswordLabel}
              placeholder="********"
              value={field.value}
              error={field.error}
              required
            />
          )}
        </ChangePassword.Field>
        <ChangePassword.Field
          name="newPassword"
          validate={[
            required(t('validation.required')),
            minLength(
              MIN_PASSWORD_LENGTH,
              t('validation.minPassword', { min: MIN_PASSWORD_LENGTH }),
            ),
          ]}
        >
          {(field, props) => (
            <TextInput
              {...props}
              type="password"
              label={newPasswordLabel}
              placeholder="********"
              value={field.value}
              error={field.error}
              required
            />
          )}
        </ChangePassword.Field>
        <ChangePassword.Field
          name="repeatNewPassword"
          validate={[
            required(t('validation.required')),
            custom$(
              value => value === getValue(changePasswordForm, 'newPassword'),
              t(`validation.passwordMatch`),
            ),
          ]}
        >
          {(field, props) => (
            <TextInput
              {...props}
              type="password"
              label={repeatNewPasswordLabel}
              placeholder="********"
              value={field.value}
              error={field.error}
              required
            />
          )}
        </ChangePassword.Field>
        <div>{changePasswordForm.response.message}</div>
        <button type="submit" disabled={changePasswordForm.submitting}>
          {t('account.changePassword')}
        </button>
      </ChangePassword.Form>
      <button type="submit">{t('account.deleteAccount')}</button>
    </>
  );
});
