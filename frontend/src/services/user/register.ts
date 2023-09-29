import { type RequestSender } from './types';

export const register = async (
  onRequest: RequestSender,
  fullName: string,
  email: string,
  password: string,
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

  const { createUser } = await onRequest(mutation, {
    input: {
      fullName,
      email,
      password,
    },
  });
  return createUser;
};
