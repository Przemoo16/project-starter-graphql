import { expect, test } from 'vitest';

import { hasProblems } from './has-problems';

test(`[hasProblems function]: returns true if problems are present`, () => {
  const data = {
    problems: [
      {
        __typename: 'test1',
      },
      {
        __typename: 'test2',
      },
    ],
  };

  const problemsPresent = hasProblems(data);

  expect(problemsPresent).toBe(true);
});

test(`[hasProblems function]: returns false if problems are not present`, () => {
  const data = {};

  const problemsPresent = hasProblems(data);

  expect(problemsPresent).toBe(false);
});
