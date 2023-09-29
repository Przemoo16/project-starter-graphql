import { type RequestSender } from './types';

export const deleteMe = async (onRequest: RequestSender) => {
  const mutation = `
    mutation DeleteMe {
      deleteMe {
        message
      }
    }
  `;

  const { deleteMe } = await onRequest(mutation);
  return deleteMe;
};
