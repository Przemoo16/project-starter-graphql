import { type DeleteMeResponse } from '~/services/graphql';

import { type RequestSender } from './types';

export const deleteMe = async (
  onRequest: RequestSender,
): Promise<DeleteMeResponse> => {
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
