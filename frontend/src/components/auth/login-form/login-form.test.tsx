import { $ } from '@builder.io/qwik';
import { createDOM } from '@builder.io/qwik/testing';
import { describe, expect, test } from 'vitest';

import { type LoginInput } from '~/services/graphql';
import { fillInput } from '~/tests/input';

import { LoginForm } from './login-form';

const ON_SUBMIT = $(async (_input: LoginInput) => {});

describe('[LoginForm Component]', () => {
  test(`doesn't display error if email passes validation`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<LoginForm onSubmit$={ON_SUBMIT} />);
    const input = screen.querySelector('#email') as HTMLInputElement;

    await fillInput(input, userEvent, 'test@email.com');
    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#email-error');
    expect(error).toBeUndefined();
  });

  test(`displays error if email is not provided`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<LoginForm onSubmit$={ON_SUBMIT} />);

    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#email-error') as HTMLDivElement;
    expect(error.textContent).toContain('fieldRequired');
  });

  test(`displays error if email is invalid`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<LoginForm onSubmit$={ON_SUBMIT} />);
    const input = screen.querySelector('#email') as HTMLInputElement;

    await fillInput(input, userEvent, 'test');
    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#email-error') as HTMLDivElement;
    expect(error.textContent).toContain('invalidEmail');
  });

  test(`doesn't display error if password passes validation`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<LoginForm onSubmit$={ON_SUBMIT} />);
    const input = screen.querySelector('#password') as HTMLInputElement;

    await fillInput(input, userEvent, 'testPassword');
    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#password-error');
    expect(error).toBeUndefined();
  });

  test(`displays error if password is not provided`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<LoginForm onSubmit$={ON_SUBMIT} />);

    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#password-error') as HTMLDivElement;
    expect(error.textContent).toContain('fieldRequired');
  });
});
