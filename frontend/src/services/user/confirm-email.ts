import { type ConfirmEmailResponse } from '~/services/graphql';

import { type RequestSender } from './types';

export const confirmEmail = async (onRequest: RequestSender, token: string) => {
  const mutation = `
    mutation ConfirmEmail($token: String!) {
      confirmEmail(token: $token) {
        ... on ConfirmEmailFailure {
          problems {
            __typename
          }
        }
      }
    }
  `;

  const { confirmEmail } = (await onRequest(mutation, {
    token,
  })) as { confirmEmail: ConfirmEmailResponse };
  return confirmEmail;
};
