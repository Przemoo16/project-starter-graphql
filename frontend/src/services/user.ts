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
    const REGISTER_MUTATION = `
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

    const { createUser } = await sendRequest(REGISTER_MUTATION, {
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
    const LOGIN_MUTATION = `
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

    const { login } = await sendRequest(LOGIN_MUTATION, {
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
  const REFRESH_TOKEN_MUTATION = `
    mutation RefreshToken($token: String!) {
      refreshToken(token: $token) {
        accessToken
        tokenType
      }
    }
  `;

  const { refreshToken } = await sendRequest(REFRESH_TOKEN_MUTATION, {
    token: localStorage.getItem('auth:refreshToken'),
  });
  localStorage.setItem('auth:accessToken', refreshToken.accessToken);
  return refreshToken;
});

export const recoverPassword = $(async (email: string): Promise<any> => {
  const RECOVER_PASSWORD_MUTATION = `
    mutation RecoverPassword($email: String!) {
      recoverPassword(email: $email) {
        message
      }
    }
  `;

  const { recoverPassword } = await sendRequest(RECOVER_PASSWORD_MUTATION, {
    email,
  });
  return recoverPassword;
});

export const resetPassword = $(
  async (token: string, password: string): Promise<any> => {
    const RESET_PASSWORD_MUTATION = `
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

    const { resetPassword } = await sendRequest(RESET_PASSWORD_MUTATION, {
      input: {
        token,
        password,
      },
    });
    return resetPassword;
  },
);

export const confirmEmail = $(async (token: string): Promise<any> => {
  const CONFIRM_EMAIL_MUTATION = `
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

  const { confirmEmail } = await sendRequest(CONFIRM_EMAIL_MUTATION, {
    token,
  });
  return confirmEmail;
});

export const getMe = $(async (): Promise<any> => {
  const GET_ME_QUERY = `
    query GetMe {
      me {
        id
      }
    }
  `;

  return await sendAuthorizedRequest(GET_ME_QUERY, {});
});

export const updateMe = $(async (fullName: string): Promise<any> => {
  const UPDATE_ME_MUTATION = `
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

  const { updateMe } = await sendAuthorizedRequest(UPDATE_ME_MUTATION, {
    input: {
      fullName,
    },
  });
  return updateMe;
});

export const changeMyPassword = $(
  async (currentPassword: string, newPassword: string): Promise<any> => {
    const CHANGE_MY_PASSWORD_MUTATION = `
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

    const { changeMyPassword } = await sendAuthorizedRequest(
      CHANGE_MY_PASSWORD_MUTATION,
      {
        input: {
          currentPassword,
          newPassword,
        },
      },
    );
    return changeMyPassword;
  },
);

export const deleteMe = $(async (): Promise<any> => {
  const DELETE_ME_MUTATION = `
    mutation DeleteMe {
      deleteMe {
        message
      }
    }
  `;

  const { deleteMe } = await sendAuthorizedRequest(DELETE_ME_MUTATION, {});
  return deleteMe;
});
