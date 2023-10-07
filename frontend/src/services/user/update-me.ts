import { type RequestSender } from './types';

export const updateMe = async (onRequest: RequestSender, fullName: string) => {
  const mutation = `
    mutation UpdateMe($input: UpdateMeInput!) {
      updateMe(input: $input) {
        ... on UpdateMeFailure {
          problems {
            __typename
          }
        }
      }
    }
  `;

  const { updateMe } = await onRequest(mutation, {
    input: {
      fullName,
    },
  });
  return updateMe;
};