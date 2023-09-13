import { isServer } from '@builder.io/qwik/build';

import { sendGraphQLRequest } from '~/libs/api/requests';

const getApiURL = (isRunningOnTheServer: boolean): string => {
  const serverApiURL =
    import.meta.env.VITE_SERVER_API_URL ?? 'http://proxy/graphql';
  const clientApiURL =
    import.meta.env.VITE_CLIENT_API_URL ?? 'http://localhost:5173/graphql';
  return isRunningOnTheServer ? serverApiURL : clientApiURL;
};

const sendRequest = async (
  query: string,
  variables: Record<string, unknown>,
): Promise<any> => {
  const response = await sendGraphQLRequest(
    getApiURL(isServer),
    query,
    variables,
  );
  const { errors, data } = await response.json();
  if (errors) {
    throw Error('Error');
  }
  return data;
};

const sendAuthorizedRequest = async (
  query: string,
  variables: Record<string, unknown>,
): Promise<any> => {
  const url = getApiURL(isServer);
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
};

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

export const register = async (
  fullName: string,
  email: string,
  password: string,
): Promise<any> =>
  await sendRequest(REGISTER_MUTATION, {
    input: {
      fullName,
      email,
      password,
    },
  });

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

export const login = async (email: string, password: string): Promise<any> => {
  // TODO: Fix any type
  const data = await sendRequest(LOGIN_MUTATION, {
    input: {
      username: email,
      password,
    },
  });
  if (!data.login.problems) {
    localStorage.setItem('auth:accessToken', data.login.accessToken);
    localStorage.setItem('auth:refreshToken', data.login.refreshToken);
  }
  return data;
};

const REFRESH_TOKEN_MUTATION = `
mutation RefreshToken($token: String!) {
    refreshToken(token: $token) {
      accessToken
      tokenType
    }
  }
`;

export const refreshToken = async (): Promise<any> => {
  // TODO: Fix any type
  const data = await sendRequest(REFRESH_TOKEN_MUTATION, {
    token: localStorage.getItem('auth:refreshToken'),
  });
  localStorage.setItem('auth:accessToken', data.refreshToken.accessToken);
  return data;
};

const RECOVER_PASSWORD_MUTATION = `
  mutation RecoverPassword($email: String!) {
    recoverPassword(email: $email) {
      message
    }
  }
`;

export const recoverPassword = async (email: string): Promise<any> =>
  await sendRequest(RECOVER_PASSWORD_MUTATION, {
    email,
  });

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

export const resetPassword = async (
  token: string,
  password: string,
): Promise<any> =>
  await sendRequest(RESET_PASSWORD_MUTATION, {
    input: {
      token,
      password,
    },
  });

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

export const confirmEmail = async (token: string): Promise<any> =>
  await sendRequest(CONFIRM_EMAIL_MUTATION, {
    token,
  });

const GET_ME_QUERY = `
  query GetMe {
    me {
      id
    }
  }
`;

export const getMe = async (): Promise<any> =>
  await sendAuthorizedRequest(GET_ME_QUERY, {});

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

export const updateMe = async (fullName: string): Promise<any> =>
  await sendAuthorizedRequest(UPDATE_ME_MUTATION, {
    input: {
      fullName,
    },
  });

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

export const changeMyPassword = async (
  currentPassword: string,
  newPassword: string,
): Promise<any> =>
  await sendAuthorizedRequest(CHANGE_MY_PASSWORD_MUTATION, {
    input: {
      currentPassword,
      newPassword,
    },
  });

const DELETE_ME_MUTATION = `
  mutation DeleteMe {
    deleteMe {
      message
    }
  }
`;

export const deleteMe = async (): Promise<any> =>
  await sendAuthorizedRequest(DELETE_ME_MUTATION, {});
