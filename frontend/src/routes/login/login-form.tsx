import { $, component$ } from '@builder.io/qwik';
import { useLocation, useNavigate } from '@builder.io/qwik-city';
import {
  email,
  FormError,
  required,
  type SubmitHandler,
  useForm,
} from '@modular-forms/qwik';
import { inlineTranslate, useSpeakContext, useTranslate } from 'qwik-speak';

import { TextInput } from '~/components/text-input/text-input';
import { isProblemPresent } from '~/libs/api/is-problem-present';
import { RouteURL } from '~/libs/api/route-url';
import { getClientRequestSender } from '~/services/requests/get-client-request-sender';
import { getClientTokenStorage } from '~/services/tokens/get-client-token-storage';
import { login } from '~/services/user/login';

type LoginFormSchema = {
  email: string;
  password: string;
};

export const LoginForm = component$(() => {
  const t = useTranslate();
  const ctx = useSpeakContext();
  const nav = useNavigate();
  const loc = useLocation();
  const [loginForm, { Form, Field }] = useForm<LoginFormSchema>({
    loader: { value: { email: '', password: '' } },
  });

  const handleSubmit = $<SubmitHandler<LoginFormSchema>>(
    async (values, _event) => {
      const { problems } = await login(
        getClientRequestSender(),
        getClientTokenStorage(),
        values.email,
        values.password,
      );

      if (problems) {
        let error = '';
        if (isProblemPresent(problems, 'UserEmailNotConfirmedProblem')) {
          error = inlineTranslate('login.emailNotConfirmed', ctx);
        } else {
          error = inlineTranslate('login.invalidCredentials', ctx);
        }
        throw new FormError<LoginFormSchema>(error);
      }

      await nav(loc.url.searchParams.get('callbackUrl') ?? RouteURL.Dashboard);
    },
  );

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
        {t('login.login')}
      </button>
    </Form>
  );
});
