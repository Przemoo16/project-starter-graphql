import { $ } from '@builder.io/qwik';
import { createDOM } from '@builder.io/qwik/testing';
import { expect, test } from 'vitest';

import { TextInput } from './text-input';

const EMPTY_CALLBACK = $(() => {});

test(`[TextInput Component]: doesn't render label`, async () => {
  const { screen, render } = await createDOM();
  const component = (
    <TextInput
      name="test"
      type="text"
      value=""
      error=""
      ref={EMPTY_CALLBACK}
      onInput$={EMPTY_CALLBACK}
      onChange$={EMPTY_CALLBACK}
      onBlur$={EMPTY_CALLBACK}
    />
  );

  await render(component);

  expect(screen.outerHTML).not.toContain('<label for="test">');
});

test(`[TextInput Component]: renders label`, async () => {
  const { screen, render } = await createDOM();
  const component = (
    <TextInput
      name="test"
      type="text"
      label="Test Label"
      value=""
      error=""
      ref={EMPTY_CALLBACK}
      onInput$={EMPTY_CALLBACK}
      onChange$={EMPTY_CALLBACK}
      onBlur$={EMPTY_CALLBACK}
    />
  );

  await render(component);

  expect(screen.outerHTML).toContain('<label for="test">Test Label </label>');
});

test(`[TextInput Component]: renders required label`, async () => {
  const { screen, render } = await createDOM();
  const component = (
    <TextInput
      name="test"
      type="text"
      label="Test Label"
      value=""
      error=""
      required
      ref={EMPTY_CALLBACK}
      onInput$={EMPTY_CALLBACK}
      onChange$={EMPTY_CALLBACK}
      onBlur$={EMPTY_CALLBACK}
    />
  );

  await render(component);

  expect(screen.outerHTML).toContain(
    '<label for="test">Test Label <span>*</span></label>',
  );
});

test(`[TextInput Component]: renders input without error`, async () => {
  const { screen, render } = await createDOM();
  const component = (
    <TextInput
      name="test"
      type="text"
      label="Test Label"
      value=""
      error=""
      ref={EMPTY_CALLBACK}
      onInput$={EMPTY_CALLBACK}
      onChange$={EMPTY_CALLBACK}
      onBlur$={EMPTY_CALLBACK}
    />
  );

  await render(component);

  expect(screen.outerHTML).toContain(
    '<input aria-errormessage="test-error" aria-invalid="false" id="test" type="text">',
  );
  expect(screen.outerHTML).not.toContain('<div id="test-error">');
});

test(`[TextInput Component]: renders input with error`, async () => {
  const { screen, render } = await createDOM();
  const component = (
    <TextInput
      name="test"
      type="text"
      label="Test Label"
      value=""
      error="Test Error"
      ref={EMPTY_CALLBACK}
      onInput$={EMPTY_CALLBACK}
      onChange$={EMPTY_CALLBACK}
      onBlur$={EMPTY_CALLBACK}
    />
  );

  await render(component);

  expect(screen.outerHTML).toContain(
    '<input aria-errormessage="test-error" aria-invalid="true" id="test" type="text"><div id="test-error">',
  );
  expect(screen.outerHTML).toContain('<div id="test-error">Test Error</div>');
});
