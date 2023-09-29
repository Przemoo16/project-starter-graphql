import { type RequestSender } from './types';

export const getMe = async (onRequest: RequestSender) => {
  const query = `
    query GetMe {
      me {
        id
        email
        fullName
      }
    }
  `;

  return await onRequest(query);
};
