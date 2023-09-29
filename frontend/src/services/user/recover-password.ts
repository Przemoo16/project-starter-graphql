import { type RequestSender } from './types';

export const recoverPassword = async (
  onRequest: RequestSender,
  email: string,
) => {
  const mutation = `
    mutation RecoverPassword($email: String!) {
      recoverPassword(email: $email) {
        message
      }
    }
  `;

  const { recoverPassword } = await onRequest(mutation, {
    email,
  });
  return recoverPassword;
};
