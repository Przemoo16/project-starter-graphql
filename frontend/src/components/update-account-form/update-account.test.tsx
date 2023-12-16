import { $ } from '@builder.io/qwik';
import { createDOM } from '@builder.io/qwik/testing';
import { describe, expect, test } from 'vitest';

import { fillInput } from '~/tests/input';

import { UpdateAccountForm } from './update-account-form';

const ON_SUBMIT = $((_fullName: string) => 'Success');
const LOADER = {
  value: { fullName: '' },
};

describe('[UpdateAccountForm Component]', () => {
  test(`displays fetched full name`, async () => {
    const { screen, render } = await createDOM();
    const loader = {
      value: { fullName: 'Test User' },
    };
    await render(<UpdateAccountForm loader={loader} onSubmit={ON_SUBMIT} />);
    const input = screen.querySelector('#fullName') as HTMLInputElement;

    expect(input.value).toEqual('Test User');
  });

  test(`doesn't display error if full name passes validation`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<UpdateAccountForm loader={LOADER} onSubmit={ON_SUBMIT} />);
    const input = screen.querySelector('#fullName') as HTMLInputElement;

    await fillInput(input, userEvent, 'Test User');
    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#fullName-error');
    expect(error).toBeUndefined();
  });

  test(`displays error if full name is not provided`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<UpdateAccountForm loader={LOADER} onSubmit={ON_SUBMIT} />);

    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#fullName-error') as HTMLDivElement;
    expect(error.innerHTML).toContain('required');
  });

  test(`displays error if full name is too long`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<UpdateAccountForm loader={LOADER} onSubmit={ON_SUBMIT} />);
    const input = screen.querySelector('#fullName') as HTMLInputElement;

    await fillInput(input, userEvent, 'T'.repeat(129));
    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#fullName-error') as HTMLDivElement;
    expect(error.innerHTML).toContain('maxFullName');
  });

  // FIXME: Enable the test after this is resolved: https://github.com/fabian-hiller/modular-forms/issues/161
  test.skip(`displays success message`, async () => {
    const { screen, render, userEvent } = await createDOM();
    const onSubmit = $(
      (_fullName: string) => 'Form has been submitted successfully',
    );
    await render(<UpdateAccountForm loader={LOADER} onSubmit={onSubmit} />);
    const fullNameInput = screen.querySelector('#fullName') as HTMLInputElement;

    await fillInput(fullNameInput, userEvent, 'Test User');
    await userEvent('button[type="submit"]', 'submit');

    expect(screen.innerHTML).toContain('Form has been submitted successfully');
  });
});
