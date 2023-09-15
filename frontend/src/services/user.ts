import { $ } from '@builder.io/qwik';
import { isServer } from '@builder.io/qwik/build';

import {
  getApiURL,
  sendAuthorizedRequest,
  sendRequest,
  sendRequestWithErrorHandling,
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
) => Promise<any>;

const ACCESS_TOKEN_STORAGE_KEY = 'auth:accessToken';
const REFRESH_TOKEN_STORAGE_KEY = 'auth:refreshToken';

const REQUEST_SENDER = $(
  async (query: string, variables?: Record<string, unknown>) => {
    const url = await getApiURL(isServer);
    const sender = async (): Promise<any> =>
      await sendRequestWithErrorHandling(url, query, sendRequest, variables);
    return await sendAuthorizedRequest(
      url,
      query,
      sender,
      async () => await getAuthHeader(localStorage),
      async () => await refreshToken(localStorage, sender),
      async () => {
        await clearTokens(localStorage);
      },
      variables,
    );
  },
);

export const userService = {
  register: $(
    async (fullName: string, email: string, password: string) =>
      await register(fullName, email, password, REQUEST_SENDER),
  ),
  login: $(
    async (email: string, password: string) =>
      await login(email, password, localStorage, REQUEST_SENDER),
  ),
  recoverPassword: $(
    async (email: string) => await recoverPassword(email, REQUEST_SENDER),
  ),
  resetPassword: $(
    async (token: string, password: string) =>
      await resetPassword(token, password, REQUEST_SENDER),
  ),
  confirmEmail: $(
    async (token: string) => await confirmEmail(token, REQUEST_SENDER),
  ),
  updateMe: $(
    async (fullName: string) => await updateMe(fullName, REQUEST_SENDER),
  ),
  changeMyPassword: $(
    async (currentPassword: string, newPassword: string) =>
      await changeMyPassword(currentPassword, newPassword, REQUEST_SENDER),
  ),
};

const getAuthHeader = $((storage: TokenStorage): Record<string, string> => {
  const accessToken = storage.getItem(ACCESS_TOKEN_STORAGE_KEY);
  return accessToken ? { Authorization: `Bearer ${accessToken}` } : {};
});

const clearTokens = $((storage: TokenStorage) => {
  storage.removeItem(ACCESS_TOKEN_STORAGE_KEY);
  storage.removeItem(REFRESH_TOKEN_STORAGE_KEY);
});

export const register = $(
  async (
    fullName: string,
    email: string,
    password: string,
    requestSender: RequestSender,
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
    email: string,
    password: string,
    storage: TokenStorage,
    requestSender: RequestSender,
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
  async (storage: TokenStorage, requestSender: RequestSender) => {
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
  async (email: string, requestSender: RequestSender) => {
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
  async (token: string, password: string, requestSender: RequestSender) => {
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
  async (token: string, requestSender: RequestSender) => {
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
  async (fullName: string, requestSender: RequestSender) => {
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
    currentPassword: string,
    newPassword: string,
    requestSender: RequestSender,
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
