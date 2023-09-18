import { $, component$, type QRL } from '@builder.io/qwik';
import {
  custom$,
  getValue,
  minLength,
  required,
  reset,
  setResponse,
  type SubmitHandler,
  useForm,
} from '@modular-forms/qwik';
import { inlineTranslate, useSpeakContext, useTranslate } from 'qwik-speak';

import { TextInput } from '~/components/text-input/text-input';

import { MIN_PASSWORD_LENGTH } from './schema-config';

export type ChangePasswordFormSchema = {
  currentPassword: string;
  newPassword: string;
  repeatNewPassword: string;
};

interface ChangePasswordFormProps {
  onSubmit: QRL<SubmitHandler<ChangePasswordFormSchema>>;
}

export const ChangePasswordForm = component$(
  ({ onSubmit }: ChangePasswordFormProps) => {
    const t = useTranslate();
    const ctx = useSpeakContext();
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
      async (values, event) => {
        await onSubmit(values, event);

        reset(changePasswordForm);
        setResponse(changePasswordForm, {
          message: inlineTranslate('account.changePasswordSuccess', ctx),
        });
      },
    );

    const currentPasswordLabel = t('account.currentPassword');
    const newPasswordLabel = t('account.newPassword');
    const repeatNewPasswordLabel = t('account.repeatNewPassword');

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
    );
  },
);
