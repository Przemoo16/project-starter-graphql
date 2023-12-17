import { isAuthenticated } from '~/libs/auth/is-authenticated';
import { type Storage } from '~/libs/storage/types';
import { type User } from '~/services/graphql';

import { type RequestSender } from './types';

export const getMe = async (
  onRequest: RequestSender,
  storage: Storage,
): Promise<User> => {
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

  const { me } = await onRequest(query);
  return me;
};
