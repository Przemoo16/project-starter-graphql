import { $ } from '@builder.io/qwik';
import { createDOM } from '@builder.io/qwik/testing';
import { describe, expect, test } from 'vitest';

import { fillInput } from '~/tests/input';

import { RecoverPasswordForm } from './recover-password-form';

const ON_SUBMIT = $(async (_email: string) => {});

describe('[RecoverPasswordForm Component]', () => {
  test(`doesn't display error if email passes validation`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<RecoverPasswordForm onSubmit$={ON_SUBMIT} />);
    const input = screen.querySelector('#email') as HTMLInputElement;

    await fillInput(input, userEvent, 'test@email.com');
    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#email-error');
    expect(error).toBeUndefined();
  });

  test(`displays error if email is not provided`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<RecoverPasswordForm onSubmit$={ON_SUBMIT} />);

    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#email-error') as HTMLDivElement;
    expect(error.textContent).toContain('fieldRequired');
  });

  test(`displays error if email is invalid`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<RecoverPasswordForm onSubmit$={ON_SUBMIT} />);
    const input = screen.querySelector('#email') as HTMLInputElement;

    await fillInput(input, userEvent, 'test');
    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#email-error') as HTMLDivElement;
    expect(error.textContent).toContain('invalidEmail');
  });

  test(`resets form after submit`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<RecoverPasswordForm onSubmit$={ON_SUBMIT} />);
    const input = screen.querySelector('#email') as HTMLInputElement;

    await fillInput(input, userEvent, 'test@email.com');
    await userEvent('button[type="submit"]', 'submit');

    expect(input.value).toEqual('');
  });

  // FIXME: Enable the test after this is resolved: https://github.com/fabian-hiller/modular-forms/issues/161
  test.skip(`displays success message`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<RecoverPasswordForm onSubmit$={ON_SUBMIT} />);
    const input = screen.querySelector('#email') as HTMLInputElement;

    await fillInput(input, userEvent, 'test@email.com');
    await userEvent('button[type="submit"]', 'submit');

    expect(screen.textContent).toContain('recoverPasswordSuccess');
  });
});
