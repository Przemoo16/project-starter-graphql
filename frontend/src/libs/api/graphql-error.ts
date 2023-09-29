interface GraphQLErrorDetails {
  message: string;
  locations: Array<{
    line: number;
    column: number;
  }>;
  path: string[];
}

export class GraphQLError extends Error {
  errors: GraphQLErrorDetails[];

  constructor(
    errors: GraphQLErrorDetails[],
    message?: string,
    options?: ErrorOptions,
  ) {
    super(message, options);
    this.errors = errors;
    Error.captureStackTrace(this, GraphQLError);
  }
}
