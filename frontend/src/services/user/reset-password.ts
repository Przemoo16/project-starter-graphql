import { type RequestSender } from './types';

export const resetPassword = async (
  onRequest: RequestSender,
  token: string,
  password: string,
) => {
  const mutation = `
      mutation ResetPassword($input: ResetPasswordInput!) {
        resetPassword(input: $input) {
          ... on ResetPasswordFailure {
            problems {
              __typename
            }
          }
        }
      }
    `;

  const { resetPassword } = await onRequest(mutation, {
    input: {
      token,
      password,
    },
  });
  return resetPassword;
};
