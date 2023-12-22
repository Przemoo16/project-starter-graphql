import {
  type ChangeMyPasswordInput,
  type ChangeMyPasswordResponse,
} from '~/services/graphql';

import { type RequestSender } from './types';

export const changeMyPassword = async (
  onRequest: RequestSender,
  input: ChangeMyPasswordInput,
) => {
  const mutation = `
      mutation ChangeMyPassword($input: ChangeMyPasswordInput!) {
        changeMyPassword(input: $input) {
          ... on ChangeMyPasswordFailure {
            problems {
              __typename
            }
          }
        }
      }
    `;

  const { changeMyPassword } = (await onRequest(mutation, {
    input,
  })) as { changeMyPassword: ChangeMyPasswordResponse };
  return changeMyPassword;
};
