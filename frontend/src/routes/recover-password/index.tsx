import { $, component$ } from '@builder.io/qwik';
import { type DocumentHead } from '@builder.io/qwik-city';
import {
  email,
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
import { REQUEST_SENDER } from '~/services/context';
import { recoverPassword } from '~/services/user';

export const head: DocumentHead = {
  title: 'runtime.recoverPassword.head.title',
};

type RecoverPasswordForm = {
  email: string;
};

export default component$(() => (
  <Speak assets={['auth', 'validation']}>
    <RecoverPassword />
  </Speak>
));

const RecoverPassword = component$(() => {
  const t = useTranslate();
  const ctx = useSpeakContext();
  const [recoverPasswordForm, { Form, Field }] = useForm<RecoverPasswordForm>({
    loader: { value: { email: '' } },
  });

  const handleSubmit = $<SubmitHandler<RecoverPasswordForm>>(
    async (values, _event) => {
      await recoverPassword(REQUEST_SENDER, values.email);

      reset(recoverPasswordForm);
      setResponse(recoverPasswordForm, {
        message: inlineTranslate('auth.recoverPasswordSuccess', ctx),
      });
    },
  );

  const emailLabel = t('auth.email');

  return (
    <Form onSubmit$={handleSubmit}>
      <Field
        name="email"
        validate={[
          required(t('validation.required')),
          email(t('validation.invalidEmail')),
        ]}
      >
        {(field, props) => (
          <TextInput
            {...props}
            type="email"
            label={emailLabel}
            placeholder="joe@example.com"
            value={field.value}
            error={field.error}
            required
          />
        )}
      </Field>
      <div>{recoverPasswordForm.response.status}</div>
      <div>{recoverPasswordForm.response.message}</div>
      <div>{recoverPasswordForm.response.data}</div>
      <button type="submit" disabled={recoverPasswordForm.submitting}>
        {t('auth.recoverPassword')}
      </button>
    </Form>
  );
});
