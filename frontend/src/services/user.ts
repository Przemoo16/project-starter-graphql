import { $ } from '@builder.io/qwik';

import { type TokenStorage } from '~/libs/tokens/storage';

type RequestSender = (
  query: string,
  variables?: Record<string, unknown>,
) => Promise<Record<string, any>>;

const ACCESS_TOKEN_STORAGE_KEY = 'accessToken';
const REFRESH_TOKEN_STORAGE_KEY = 'refreshToken';

export const getAuthHeader = $(async (storage: TokenStorage) => {
  const accessToken = storage.get(ACCESS_TOKEN_STORAGE_KEY);
  const headers: Record<string, string> = accessToken
    ? { Authorization: `Bearer ${accessToken}` }
    : {};
  return headers;
});

export const clearTokens = $((storage: TokenStorage) => {
  storage.remove(ACCESS_TOKEN_STORAGE_KEY);
  storage.remove(REFRESH_TOKEN_STORAGE_KEY);
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
      storage.set(ACCESS_TOKEN_STORAGE_KEY, login.accessToken);
      storage.set(REFRESH_TOKEN_STORAGE_KEY, login.refreshToken);
    }
    return login;
  },
);

export const logout = $(async (storage: TokenStorage) => {
  await clearTokens(storage);
});

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
      token: storage.get(REFRESH_TOKEN_STORAGE_KEY),
    });
    storage.set(ACCESS_TOKEN_STORAGE_KEY, refreshToken.accessToken);
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
        email
        fullName
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
