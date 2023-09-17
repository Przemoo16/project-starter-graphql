interface Problem {
  __typename: string;
}

export const isProblemPresent = (problems: Problem[], type: string) =>
  problems.some(problem => problem.__typename === type);

export interface GraphQLError {
  message: string;
  locations: Array<{
    line: number;
    column: number;
  }>;
  path: string[];
}

export class RequestError extends Error {
  errors: GraphQLError[];

  constructor(
    errors: GraphQLError[],
    message?: string,
    options?: ErrorOptions,
  ) {
    super(message, options);
    this.errors = errors;
    Error.captureStackTrace(this, RequestError);
  }
}
