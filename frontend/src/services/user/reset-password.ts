import { type ResetPasswordResponse } from '~/services/graphql';

import { type RequestSender } from './types';

export const resetPassword = async (
  onRequest: RequestSender,
  token: string,
  password: string,
): Promise<ResetPasswordResponse> => {
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
