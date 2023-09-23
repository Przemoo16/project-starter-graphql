import { createDOM } from '@builder.io/qwik/testing';
import { expect, test } from 'vitest';

import { TitleHead } from './title-head';

test(`[TitleHead Component]: displays only the app name if the page title is missing`, async () => {
  const { screen, render } = await createDOM();
  const component = <TitleHead appName="Test App" pageTitle="" />;

  await render(component);

  expect(screen.outerHTML).toContain('<title>Test App</title>');
});

test(`[TitleHead Component]: displays both the app name and the page title`, async () => {
  const { screen, render } = await createDOM();
  const component = <TitleHead appName="Test App" pageTitle="Test Page" />;

  await render(component);

  expect(screen.outerHTML).toContain('<title>Test Page | Test App</title>');
});