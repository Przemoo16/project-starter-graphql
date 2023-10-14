import { type Storage } from '~/libs/storage/types';

import { isAuthenticated } from './is-authenticated';
import { type RequestSender } from './types';

export const getMe = async (onRequest: RequestSender, storage: Storage) => {
  if (!isAuthenticated(storage)) {
    throw new Error('User is not authenticated');
  }

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
