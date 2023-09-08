import { isServer } from '@builder.io/qwik/build';

const sendGraphQLrequest = async (
  query: string,
  variables: Record<string, unknown>,
): Promise<any> => {
  const response = await fetch(getApiURL(), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      variables,
    }),
  });
  return await response.json();
};

const getApiURL = (): string => {
  const serverApiURL =
    import.meta.env.VITE_SERVER_API_URL || 'http://proxy/graphql';
  const clientApiURL =
    import.meta.env.VITE_CLIENT_API_URL || 'http://localhost:5173/graphql';
  return isServer ? serverApiURL : clientApiURL;
};

const REGISTER_QUERY = `
  mutation CreateUser($input: UserCreateInput!) {
    createUser(input: $input) {
      ... on CreateUserFailure {
        problems {
          __typename
          ... on Problem {
            message
          }
        }
      }
    }
  }
`;

export const register = async (
  fullName: string,
  email: string,
  password: string,
): Promise<any> => {
  // TODO: Fix any type
  const response = await sendGraphQLrequest(REGISTER_QUERY, {
    input: {
      fullName,
      email,
      password,
    },
  });
  return response.data;
};
