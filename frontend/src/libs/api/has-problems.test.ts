import { describe, expect, test } from 'vitest';

import { hasProblems } from './has-problems';

describe('[hasProblems function]', () => {
  test(`returns true if problems are present`, () => {
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

  test(`returns false if problems are not present`, () => {
    const data = {};

    const problemsPresent = hasProblems(data);

    expect(problemsPresent).toBe(false);
  });
});
