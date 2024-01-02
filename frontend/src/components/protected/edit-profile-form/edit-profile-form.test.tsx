import { $ } from '@builder.io/qwik';
import { createDOM } from '@builder.io/qwik/testing';
import { describe, expect, test } from 'vitest';

import { type UpdateMeInput } from '~/services/graphql';
import { fillInput } from '~/tests/input';

import { EditProfileForm } from './edit-profile-form';

const LOADER = {
  value: { fullName: 'Test User' },
};
const ON_SUBMIT = $(async (_input: UpdateMeInput) => ({
  fullName: 'Updated User',
}));

describe('[EditProfileForm Component]', () => {
  test(`displays fetched full name`, async () => {
    const { screen, render } = await createDOM();
    const loader = {
      value: { fullName: 'Test User' },
    };
    await render(<EditProfileForm loader={loader} onSubmit$={ON_SUBMIT} />);
    const input = screen.querySelector('#fullName') as HTMLInputElement;

    expect(input.value).toEqual('Test User');
  });

  test(`doesn't display error if full name passes validation`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<EditProfileForm loader={LOADER} onSubmit$={ON_SUBMIT} />);
    const input = screen.querySelector('#fullName') as HTMLInputElement;

    await fillInput(input, userEvent, 'Updated User');
    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#fullName-error');
    expect(error).toBeUndefined();
  });

  test(`displays error if full name is not provided`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<EditProfileForm loader={LOADER} onSubmit$={ON_SUBMIT} />);
    const input = screen.querySelector('#fullName') as HTMLInputElement;

    await fillInput(input, userEvent, '');
    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#fullName-error') as HTMLDivElement;
    expect(error.textContent).toContain('fieldRequired');
  });

  test(`displays error if full name is too long`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<EditProfileForm loader={LOADER} onSubmit$={ON_SUBMIT} />);
    const input = screen.querySelector('#fullName') as HTMLInputElement;

    await fillInput(input, userEvent, 'T'.repeat(129));
    await userEvent('button[type="submit"]', 'submit');

    const error = screen.querySelector('#fullName-error') as HTMLDivElement;
    expect(error.textContent).toContain('fullNameTooLong');
  });

  test(`doesn't send unchanged values`, async () => {
    const { render, userEvent } = await createDOM();
    const sentData: Record<string, string | undefined | null> = {
      sentFullName: undefined,
    };
    const onSubmit = $(async ({ fullName }: UpdateMeInput) => {
      sentData.sentFullName = fullName;
      return {
        fullName: 'Test User',
      };
    });
    await render(<EditProfileForm loader={LOADER} onSubmit$={onSubmit} />);

    await userEvent('button[type="submit"]', 'submit');

    expect(sentData.sentFullName).toBeUndefined();
  });

  test(`sends changed values`, async () => {
    const { screen, render, userEvent } = await createDOM();
    const sentData: Record<string, string | undefined | null> = {
      sentFullName: undefined,
    };
    const onSubmit = $(async ({ fullName }: UpdateMeInput) => {
      sentData.sentFullName = fullName;
      return {
        fullName: 'Updated User',
      };
    });
    await render(<EditProfileForm loader={LOADER} onSubmit$={onSubmit} />);
    const input = screen.querySelector('#fullName') as HTMLInputElement;

    await fillInput(input, userEvent, 'Updated User');
    await userEvent('button[type="submit"]', 'submit');

    expect(sentData.sentFullName).toEqual('Updated User');
  });

  test(`displays updated values from the response`, async () => {
    const { screen, render, userEvent } = await createDOM();
    const onSubmit = $(async (_input: UpdateMeInput) => {
      return {
        fullName: 'Updated User',
      };
    });
    await render(<EditProfileForm loader={LOADER} onSubmit$={onSubmit} />);
    const input = screen.querySelector('#fullName') as HTMLInputElement;

    await userEvent('button[type="submit"]', 'submit');

    expect(input.value).toEqual('Updated User');
  });

  // FIXME: Enable the test after this is resolved: https://github.com/fabian-hiller/modular-forms/issues/161
  test.skip(`displays success message`, async () => {
    const { screen, render, userEvent } = await createDOM();
    await render(<EditProfileForm loader={LOADER} onSubmit$={ON_SUBMIT} />);
    const input = screen.querySelector('#fullName') as HTMLInputElement;

    await fillInput(input, userEvent, 'Test User');
    await userEvent('button[type="submit"]', 'submit');

    expect(screen.textContent).toContain('profileSaved');
  });
});
