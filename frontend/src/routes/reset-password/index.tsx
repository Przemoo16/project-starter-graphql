import { $, component$ } from '@builder.io/qwik';
import { type DocumentHead, useLocation } from '@builder.io/qwik-city';
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
import {
  inlineTranslate,
  Speak,
  useSpeakContext,
  useTranslate,
} from 'qwik-speak';

import { TextInput } from '~/components/text-input/text-input';
import { MIN_PASSWORD_LENGTH } from '~/constants';
import { REQUEST_SENDER } from '~/services/context';
import { resetPassword } from '~/services/user';

export const head: DocumentHead = {
  title: 'runtime.resetPassword.head.title',
};

type ResetPasswordForm = {
  password: string;
  repeatPassword: string;
};

export default component$(() => (
  <Speak assets={['auth', 'validation']}>
    <ResetPassword />
  </Speak>
));

const ResetPassword = component$(() => {
  const t = useTranslate();
  const ctx = useSpeakContext();
  const loc = useLocation();
  const [resetPasswordForm, { Form, Field }] = useForm<ResetPasswordForm>({
    loader: { value: { password: '', repeatPassword: '' } },
  });

  const handleSubmit = $<SubmitHandler<ResetPasswordForm>>(
    async (values, _event) => {
      const { problems } = await resetPassword(
        REQUEST_SENDER,
        loc.url.searchParams.get('token') ?? '',
        values.password,
      );

      if (problems) {
        throw new FormError<ResetPasswordForm>(
          inlineTranslate('auth.resetPasswordError', ctx),
        );
      }

      reset(resetPasswordForm);
      setResponse(resetPasswordForm, {
        message: inlineTranslate('auth.resetPasswordSuccess', ctx),
      });
    },
  );

  const passwordLabel = t('auth.password');
  const repeatPasswordLabel = t('auth.repeatPassword');

  return (
    <Form onSubmit$={handleSubmit}>
      <Field
        name="password"
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
            label={passwordLabel}
            placeholder="********"
            value={field.value}
            error={field.error}
            required
          />
        )}
      </Field>
      <Field
        name="repeatPassword"
        validate={[
          required(t('validation.required')),
          custom$(
            value => value === getValue(resetPasswordForm, 'password'),
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
      <div>{resetPasswordForm.response.message}</div>
      <button type="submit" disabled={resetPasswordForm.submitting}>
        {t('auth.resetPassword')}
      </button>
    </Form>
  );
});
