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
import { inlineTranslate } from 'qwik-speak';

import { TextInput } from '~/components/text-input/text-input';
import { MIN_PASSWORD_LENGTH } from '~/routes/schema-config';

export type ChangePasswordFormSchema = {
  currentPassword: string;
  newPassword: string;
  repeatNewPassword: string;
};

interface ChangePasswordFormProps {
  onSubmit: QRL<
    (currentPassword: string, newPassword: string) => Promise<string>
  >;
}

export const ChangePasswordForm = component$(
  ({ onSubmit }: ChangePasswordFormProps) => {
    const t = inlineTranslate();
    const [changePasswordForm, { Form, Field }] =
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
      async ({ currentPassword, newPassword }, _event) => {
        const message = await onSubmit(currentPassword, newPassword);
        reset(changePasswordForm);
        setResponse(changePasswordForm, {
          message,
        });
      },
    );

    const currentPasswordLabel = t('changePassword.currentPassword');
    const newPasswordLabel = t('changePassword.newPassword');
    const repeatPasswordLabel = t('auth.repeatPassword');

    return (
      <Form onSubmit$={handleSubmit}>
        <Field
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
        </Field>
        <Field
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
        </Field>
        <Field
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
        </Field>
        <div>{changePasswordForm.response.message}</div>
        <button type="submit" disabled={changePasswordForm.submitting}>
          {t('changePassword.changePassword')}
        </button>
      </Form>
    );
  },
);