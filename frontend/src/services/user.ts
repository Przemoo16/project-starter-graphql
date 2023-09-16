import { $ } from '@builder.io/qwik';
import { isServer } from '@builder.io/qwik/build';

import {
  fetchAdapter,
  getApiURL,
  sendAuthorizedRequest,
  sendRequest,
} from '~/libs/api/requests';

interface TokenStorage {
  getItem: (key: string) => string | null;
  setItem: (key: string, value: string) => void;
  removeItem: (key: string) => void;
}

type RequestSender = (
  query: string,
  variables?: Record<string, unknown>,
  headers?: Record<string, string>,
) => Promise<Record<string, any>>;

const ACCESS_TOKEN_STORAGE_KEY = 'auth:accessToken';
const REFRESH_TOKEN_STORAGE_KEY = 'auth:refreshToken';

const REQUEST_SENDER = $(
  async (query: string, variables?: Record<string, unknown>) => {
    const url = await getApiURL(isServer);
    return await sendAuthorizedRequest(
      fetchAdapter,
      url,
      query,
      variables,
      async () => await getAuthHeader(localStorage),
      async () =>
        await refreshToken(
          await sendRequest(fetchAdapter, url, query, variables),
          localStorage,
        ),
      async () => {
        await clearTokens(localStorage);
      },
    );
  },
);

export const userService = {
  register: $(
    async (fullName: string, email: string, password: string) =>
      await register(REQUEST_SENDER, fullName, email, password),
  ),
  login: $(
    async (email: string, password: string) =>
      await login(REQUEST_SENDER, localStorage, email, password),
  ),
  recoverPassword: $(
    async (email: string) => await recoverPassword(REQUEST_SENDER, email),
  ),
  resetPassword: $(
    async (token: string, password: string) =>
      await resetPassword(REQUEST_SENDER, token, password),
  ),
  confirmEmail: $(
    async (token: string) => await confirmEmail(REQUEST_SENDER, token),
  ),
  updateMe: $(
    async (fullName: string) => await updateMe(REQUEST_SENDER, fullName),
  ),
  changeMyPassword: $(
    async (currentPassword: string, newPassword: string) =>
      await changeMyPassword(REQUEST_SENDER, currentPassword, newPassword),
  ),
};

export const getAuthHeader = $(
  async (storage: TokenStorage): Promise<Record<string, string>> => {
    const accessToken = storage.getItem(ACCESS_TOKEN_STORAGE_KEY);
    return accessToken ? { Authorization: `Bearer ${accessToken}` } : {};
  },
);

export const clearTokens = $((storage: TokenStorage) => {
  storage.removeItem(ACCESS_TOKEN_STORAGE_KEY);
  storage.removeItem(REFRESH_TOKEN_STORAGE_KEY);
});

export const register = $(
  async (
    requestSender: RequestSender,
    fullName: string,
    email: string,
    password: string,
  ) => {
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

    const { createUser } = await requestSender(mutation, {
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
  async (
    requestSender: RequestSender,
    storage: TokenStorage,
    email: string,
    password: string,
  ) => {
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

    const { login } = await requestSender(mutation, {
      input: {
        username: email,
        password,
      },
    });
    if (!login.problems) {
      storage.setItem(ACCESS_TOKEN_STORAGE_KEY, login.accessToken);
      storage.setItem(REFRESH_TOKEN_STORAGE_KEY, login.refreshToken);
    }
    return login;
  },
);

export const refreshToken = $(
  async (requestSender: RequestSender, storage: TokenStorage) => {
    const mutation = `
    mutation RefreshToken($token: String!) {
      refreshToken(token: $token) {
        accessToken
        tokenType
      }
    }
  `;

    const { refreshToken } = await requestSender(mutation, {
      token: storage.getItem(REFRESH_TOKEN_STORAGE_KEY),
    });
    storage.setItem(ACCESS_TOKEN_STORAGE_KEY, refreshToken.accessToken);
    return refreshToken;
  },
);

export const recoverPassword = $(
  async (requestSender: RequestSender, email: string) => {
    const mutation = `
    mutation RecoverPassword($email: String!) {
      recoverPassword(email: $email) {
        message
      }
    }
  `;

    const { recoverPassword } = await requestSender(mutation, {
      email,
    });
    return recoverPassword;
  },
);

export const resetPassword = $(
  async (requestSender: RequestSender, token: string, password: string) => {
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

    const { resetPassword } = await requestSender(mutation, {
      input: {
        token,
        password,
      },
    });
    return resetPassword;
  },
);

export const confirmEmail = $(
  async (requestSender: RequestSender, token: string) => {
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

    const { confirmEmail } = await requestSender(mutation, {
      token,
    });
    return confirmEmail;
  },
);

export const getMe = $(async (requestSender: RequestSender) => {
  const query = `
    query GetMe {
      me {
        id
      }
    }
  `;

  return await requestSender(query);
});

export const updateMe = $(
  async (requestSender: RequestSender, fullName: string) => {
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

    const { updateMe } = await requestSender(mutation, {
      input: {
        fullName,
      },
    });
    return updateMe;
  },
);

export const changeMyPassword = $(
  async (
    requestSender: RequestSender,
    currentPassword: string,
    newPassword: string,
  ) => {
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

    const { changeMyPassword } = await requestSender(mutation, {
      input: {
        currentPassword,
        newPassword,
      },
    });
    return changeMyPassword;
  },
);

export const deleteMe = $(async (requestSender: RequestSender) => {
  const mutation = `
    mutation DeleteMe {
      deleteMe {
        message
      }
    }
  `;

  const { deleteMe } = await requestSender(mutation);
  return deleteMe;
});
