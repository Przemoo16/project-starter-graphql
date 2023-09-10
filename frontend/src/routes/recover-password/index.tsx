import { $, component$ } from '@builder.io/qwik';
import { type DocumentHead, routeLoader$ } from '@builder.io/qwik-city';
import {
  email,
  type InitialValues,
  required,
  type SubmitHandler,
  useForm,
} from '@modular-forms/qwik';
import { Speak, useTranslate } from 'qwik-speak';

import { TextInput } from '~/components/text-input/text-input';
import { recoverPassword } from '~/services/user';

export const head: DocumentHead = {
  title: 'runtime.recoverPassword.head.title',
};

type RecoverPasswordForm = {
  email: string;
};

export const useFormLoader = routeLoader$<InitialValues<RecoverPasswordForm>>(
  () => ({
    email: '',
  }),
);

export default component$(() => (
  <Speak assets={['auth', 'validation']}>
    <RecoverPassword />
  </Speak>
));

const RecoverPassword = component$(() => {
  const t = useTranslate();
  const [recoverPasswordForm, { Form, Field }] = useForm<RecoverPasswordForm>({
    loader: useFormLoader(),
  });

  const handleSubmit = $<SubmitHandler<RecoverPasswordForm>>(
    async (values, _event) => {
      await recoverPassword(values.email);
    },
  );

  const emailLabel = t('auth.email');
  const recoverPasswordSubmitted = t('auth.recoverPasswordSubmitted');

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
      {recoverPasswordForm.submitted && <div>{recoverPasswordSubmitted}</div>}
      <button type="submit" disabled={recoverPasswordForm.submitting}>
        {t('auth.recoverPassword')}
      </button>
    </Form>
  );
});
