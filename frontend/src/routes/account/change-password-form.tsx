import { $, component$ } from '@builder.io/qwik';
import {
  custom$,
  FormError,
  getValue,
  minLength,
  required,
  reset,
  setResponse,
  type SubmitHandler,
  useForm,
} from '@modular-forms/qwik';
import { inlineTranslate } from 'qwik-speak';

import { TextInput } from '~/components/text-input/text-input';
import { isProblemPresent } from '~/libs/api/is-problem-present';
import { MIN_PASSWORD_LENGTH } from '~/routes/schema-config';
import { getClientRequestSender } from '~/services/requests/get-client-request-sender';
import { changeMyPassword } from '~/services/user/change-my-password';

type ChangePasswordFormSchema = {
  currentPassword: string;
  newPassword: string;
  repeatNewPassword: string;
};

export const ChangePasswordForm = component$(() => {
  const t = inlineTranslate();
  const [changePasswordForm, ChangePassword] =
    useForm<ChangePasswordFormSchema>({
      loader: {
        value: {
          currentPassword: '',
          newPassword: '',
          repeatNewPassword: '',
        },
      },
    });

  const handleSubmit = $<SubmitHandler<ChangePasswordFormSchema>>(
    async (values, _event) => {
      const t = inlineTranslate();

      const data = await changeMyPassword(
        getClientRequestSender(),
        values.currentPassword,
        values.newPassword,
      );

      if ('problems' in data) {
        let error = '';
        if (isProblemPresent(data.problems, 'InvalidPasswordProblem')) {
          error = t('changePassword.invalidCurrentPassword');
        } else {
          error = t('changePassword.changePasswordError');
        }
        throw new FormError<ChangePasswordFormSchema>(error);
      }

      reset(changePasswordForm);
      setResponse(changePasswordForm, {
        message: t('changePassword.changePasswordSuccess'),
      });
    },
  );

  const currentPasswordLabel = t('changePassword.currentPassword');
  const newPasswordLabel = t('changePassword.newPassword');
  const repeatPasswordLabel = t('auth.repeatPassword');

  return (
    <ChangePassword.Form onSubmit$={handleSubmit}>
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
            label={repeatPasswordLabel}
            placeholder="********"
            value={field.value}
            error={field.error}
            required
          />
        )}
      </ChangePassword.Field>
      <div>{changePasswordForm.response.message}</div>
      <button type="submit" disabled={changePasswordForm.submitting}>
        {t('changePassword.changePassword')}
      </button>
    </ChangePassword.Form>
  );
});
