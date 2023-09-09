interface Problem {
  __typename: string;
}

export const isProblemPresent = (problems: Problem[], type: string): boolean =>
  problems.some(problem => problem.__typename === type);
