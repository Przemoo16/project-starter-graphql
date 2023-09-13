import { $ } from '@builder.io/qwik';
import { isServer } from '@builder.io/qwik/build';

import { sendGraphQLRequest } from '~/libs/api/requests';

const getApiURL = $((isRunningOnTheServer: boolean): string => {
  const serverApiURL =
    import.meta.env.VITE_SERVER_API_URL ?? 'http://proxy/graphql';
  const clientApiURL =
    import.meta.env.VITE_CLIENT_API_URL ?? 'http://localhost:5173/graphql';
  return isRunningOnTheServer ? serverApiURL : clientApiURL;
});

const sendRequest = $(
  async (query: string, variables: Record<string, unknown>): Promise<any> => {
    const response = await sendGraphQLRequest(
      await getApiURL(isServer),
      query,
      variables,
    );
    const { errors, data } = await response.json();
    if (errors) {
      throw Error('Error');
    }
    return data;
  },
);

const sendAuthorizedRequest = $(
  async (query: string, variables: Record<string, unknown>): Promise<any> => {
    const url = await getApiURL(isServer);
    const accessToken = localStorage.getItem('auth:accessToken');
    const headers: Record<string, string> = accessToken
      ? { Authorization: `Bearer ${accessToken}` }
      : {};

    const response = await sendGraphQLRequest(url, query, variables, headers);
    const { errors, data } = await response.json();

    if (errors) {
      if (errors.some((error: any) => error.message === 'Invalid token')) {
        try {
          await refreshToken();
        } catch (error) {
          localStorage.removeItem('auth:accessToken');
          localStorage.removeItem('auth:refreshToken');
        }
        const originalRequest = await sendGraphQLRequest(
          url,
          query,
          variables,
          headers,
        );
        const { errors, data } = await originalRequest.json();
        if (errors) {
          throw Error('Error');
        }
        return data;
      }
      throw Error('Error');
    }
    return data;
  },
);

export const register = $(
  async (fullName: string, email: string, password: string): Promise<any> => {
    const mutation = `
      mutation CreateUser($input: UserCreateInput!) {
        createUser(input: $input) {
          ... on CreateUserFailure {
            problems {
              __typename
            }
          }
        }
      }
    `;

    const { createUser } = await sendRequest(mutation, {
      input: {
        fullName,
        email,
        password,
      },
    });
    return createUser;
  },
);

export const login = $(
  async (email: string, password: string): Promise<any> => {
    const mutation = `
      mutation Login($input: LoginInput!) {
        login(input: $input) {
          ... on LoginSuccess {
            accessToken
            refreshToken
          }
          ... on LoginFailure {
            problems {
              __typename
            }
          }
        }
      }
    `;

    const { login } = await sendRequest(mutation, {
      input: {
        username: email,
        password,
      },
    });
    if (!login.problems) {
      localStorage.setItem('auth:accessToken', login.accessToken);
      localStorage.setItem('auth:refreshToken', login.refreshToken);
    }
    return login;
  },
);

export const refreshToken = $(async (): Promise<any> => {
  const mutation = `
    mutation RefreshToken($token: String!) {
      refreshToken(token: $token) {
        accessToken
        tokenType
      }
    }
  `;

  const { refreshToken } = await sendRequest(mutation, {
    token: localStorage.getItem('auth:refreshToken'),
  });
  localStorage.setItem('auth:accessToken', refreshToken.accessToken);
  return refreshToken;
});

export const recoverPassword = $(async (email: string): Promise<any> => {
  const mutation = `
    mutation RecoverPassword($email: String!) {
      recoverPassword(email: $email) {
        message
      }
    }
  `;

  const { recoverPassword } = await sendRequest(mutation, {
    email,
  });
  return recoverPassword;
});

export const resetPassword = $(
  async (token: string, password: string): Promise<any> => {
    const mutation = `
      mutation ResetPassword($input: ResetPasswordInput!) {
        resetPassword(input: $input) {
          ... on ResetPasswordFailure {
            problems {
              __typename
            }
          }
        }
      }
    `;

    const { resetPassword } = await sendRequest(mutation, {
      input: {
        token,
        password,
      },
    });
    return resetPassword;
  },
);

export const confirmEmail = $(async (token: string): Promise<any> => {
  const mutation = `
    mutation ConfirmEmail($token: String!) {
      confirmEmail(token: $token) {
        ... on ConfirmEmailFailure {
          problems {
            __typename
          }
        }
      }
    }
  `;

  const { confirmEmail } = await sendRequest(mutation, {
    token,
  });
  return confirmEmail;
});

export const getMe = $(async (): Promise<any> => {
  const query = `
    query GetMe {
      me {
        id
      }
    }
  `;

  return await sendAuthorizedRequest(query, {});
});

export const updateMe = $(async (fullName: string): Promise<any> => {
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

  const { updateMe } = await sendAuthorizedRequest(mutation, {
    input: {
      fullName,
    },
  });
  return updateMe;
});

export const changeMyPassword = $(
  async (currentPassword: string, newPassword: string): Promise<any> => {
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

    const { changeMyPassword } = await sendAuthorizedRequest(mutation, {
      input: {
        currentPassword,
        newPassword,
      },
    });
    return changeMyPassword;
  },
);

export const deleteMe = $(async (): Promise<any> => {
  const mutation = `
    mutation DeleteMe {
      deleteMe {
        message
      }
    }
  `;

  const { deleteMe } = await sendAuthorizedRequest(mutation, {});
  return deleteMe;
});
