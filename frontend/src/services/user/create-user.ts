import {
  type CreateUserResponse,
  type UserCreateInput,
} from '~/services/graphql';

import { type RequestSender } from './types';

export const createUser = async (
  onRequest: RequestSender,
  input: UserCreateInput,
) => {
  const mutation = `
      mutation CreateUser($input: UserCreateInput!) {
        createUser(input: $input) {
          ... on CreateUserFailure {
            problems {
              __typename
            }
          }
        }
      }
    `;

  const { createUser } = (await onRequest(mutation, {
    input,
  })) as { createUser: CreateUserResponse };
  return createUser;
};
