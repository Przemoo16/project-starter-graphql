import { $, component$ } from '@builder.io/qwik';
import { routeLoader$ } from '@builder.io/qwik-city';
import {
  email,
  type InitialValues,
  required,
  type SubmitHandler,
  useForm,
} from '@modular-forms/qwik';
import { Speak, useTranslate } from 'qwik-speak';

import { TextInput } from '~/components/text-input/text-input';

export const useFormLoader = routeLoader$<InitialValues<RecoverPasswordForm>>(
  () => ({
    email: '',
  }),
);

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
  const [, { Form, Field }] = useForm<RecoverPasswordForm>({
    loader: useFormLoader(),
  });

  const handleSubmit = $<SubmitHandler<RecoverPasswordForm>>(
    (values, event) => {
      // Runs on client
      console.log(values);
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
      <button type="submit">{t('auth.recoverPassword')}</button>
    </Form>
  );
});
