import { $, component$ } from '@builder.io/qwik';
import {
  type DocumentHead,
  routeLoader$,
  useNavigate,
} from '@builder.io/qwik-city';
import {
  email,
  FormError,
  type InitialValues,
  required,
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
import { isProblemPresent } from '~/libs/api/errors';
import { login } from '~/services/user';

export const head: DocumentHead = {
  title: 'runtime.login.head.title',
};

type LoginForm = {
  email: string;
  password: string;
};

export const useFormLoader = routeLoader$<InitialValues<LoginForm>>(() => ({
  email: '',
  password: '',
}));

export default component$(() => (
  <Speak assets={['auth', 'validation']}>
    <Login />
  </Speak>
));

const Login = component$(() => {
  const t = useTranslate();
  const ctx = useSpeakContext();
  const nav = useNavigate();
  const [loginForm, { Form, Field }] = useForm<LoginForm>({
    loader: useFormLoader(),
  });

  const handleSubmit = $<SubmitHandler<LoginForm>>(async (values, _event) => {
    const {
      login: { problems },
    } = await login(values.email, values.password);

    if (!problems) {
      await nav('/dashboard');
    }

    let error = '';
    if (isProblemPresent(problems, 'UserNotConfirmedProblem')) {
      error = inlineTranslate('auth.userNotConfirmed', ctx);
    } else {
      error = inlineTranslate('auth.invalidCredentials', ctx);
    }
    throw new FormError<LoginForm>(error);
  });

  const emailLabel = t('auth.email');
  const passwordLabel = t('auth.password');

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
      <Field name="password" validate={[required(t('validation.required'))]}>
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
      <div>{loginForm.response.message}</div>
      <button type="submit" disabled={loginForm.submitting}>
        {t('auth.loginButton')}
      </button>
    </Form>
  );
});
