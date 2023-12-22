import { type UpdateMeInput, type UpdateMeResponse } from '~/services/graphql';

import { type RequestSender } from './types';

export const updateMe = async (
  onRequest: RequestSender,
  input: UpdateMeInput,
) => {
  const mutation = `
    mutation UpdateMe($input: UpdateMeInput!) {
      updateMe(input: $input) {
        ... on User {
            fullName
          }
        ... on UpdateMeFailure {
          problems {
            __typename
          }
        }
      }
    }
  `;

  const { updateMe } = (await onRequest(mutation, {
    input,
  })) as { updateMe: UpdateMeResponse };
  return updateMe;
};
