import { type RequestSender } from './types';

export const changeMyPassword = async (
  onRequest: RequestSender,
  currentPassword: string,
  newPassword: string,
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

  const { changeMyPassword } = await onRequest(mutation, {
    input: {
      currentPassword,
      newPassword,
    },
  });
  return changeMyPassword;
};
