import { createDOM } from '@builder.io/qwik/testing';
import { describe, expect, test } from 'vitest';

import { TitleHead } from './title-head';

describe('[TitleHead Component]', () => {
  test(`displays only the app name if the page title is missing`, async () => {
    const { screen, render } = await createDOM();

    await render(<TitleHead appName="Test App" pageTitle="" />);

    const title = screen.querySelector('title') as HTMLTitleElement;
    expect(title.textContent).toEqual('Test App');
  });

  test(`displays both the app name and the page title`, async () => {
    const { screen, render } = await createDOM();

    await render(<TitleHead appName="Test App" pageTitle="Test Page" />);

    const title = screen.querySelector('title') as HTMLTitleElement;
    expect(title.textContent).toEqual('Test Page | Test App');
  });
});
