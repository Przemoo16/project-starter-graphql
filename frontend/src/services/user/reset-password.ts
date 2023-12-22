import {
  type ResetPasswordInput,
  type ResetPasswordResponse,
} from '~/services/graphql';

import { type RequestSender } from './types';

export const resetPassword = async (
  onRequest: RequestSender,
  input: ResetPasswordInput,
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

  const { resetPassword } = (await onRequest(mutation, {
    input,
  })) as { resetPassword: ResetPasswordResponse };
  return resetPassword;
};
