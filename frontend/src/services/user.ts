import { type TokenStorage } from '~/libs/tokens/storage';

type RequestSender = (
  query: string,
  variables?: Record<string, unknown>,
) => Promise<Record<string, any>>;

const ACCESS_TOKEN_STORAGE_KEY = 'accessToken';
const REFRESH_TOKEN_STORAGE_KEY = 'refreshToken';

export const isAuthorized = (storage: TokenStorage) => {
  return Boolean(
    storage.get(ACCESS_TOKEN_STORAGE_KEY) ??
      storage.get(REFRESH_TOKEN_STORAGE_KEY),
  );
};

export const getAuthHeader = (storage: TokenStorage) => {
  const accessToken = storage.get(ACCESS_TOKEN_STORAGE_KEY);
  const headers: Record<string, string> = accessToken
    ? { Authorization: `Bearer ${accessToken}` }
    : {};
  return headers;
};

export const clearTokens = (storage: TokenStorage) => {
  storage.remove(ACCESS_TOKEN_STORAGE_KEY);
  storage.remove(REFRESH_TOKEN_STORAGE_KEY);
};

export const register = async (
  onRequest: RequestSender,
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

  const { createUser } = await onRequest(mutation, {
    input: {
      fullName,
      email,
      password,
    },
  });
  return createUser;
};

export const login = async (
  onRequest: RequestSender,
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

  const { login } = await onRequest(mutation, {
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
};

export const refreshToken = async (
  onRequest: RequestSender,
  storage: TokenStorage,
) => {
  const mutation = `
    mutation RefreshToken($token: String!) {
      refreshToken(token: $token) {
        accessToken
        tokenType
      }
    }
  `;

  const token = storage.get(REFRESH_TOKEN_STORAGE_KEY);
  if (!token) {
    throw new Error('No refresh token in the storage to perform refreshing');
  }
  const { refreshToken } = await onRequest(mutation, {
    token,
  });
  storage.set(ACCESS_TOKEN_STORAGE_KEY, refreshToken.accessToken);
  // Write the token again to extend the storage expiration
  storage.set(REFRESH_TOKEN_STORAGE_KEY, token);
  return refreshToken;
};

export const logout = (storage: TokenStorage, onRedirect: () => void) => {
  clearTokens(storage);
  onRedirect();
};

export const recoverPassword = async (
  onRequest: RequestSender,
  email: string,
) => {
  const mutation = `
    mutation RecoverPassword($email: String!) {
      recoverPassword(email: $email) {
        message
      }
    }
  `;

  const { recoverPassword } = await onRequest(mutation, {
    email,
  });
  return recoverPassword;
};

export const resetPassword = async (
  onRequest: RequestSender,
  token: string,
  password: string,
) => {
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

  const { resetPassword } = await onRequest(mutation, {
    input: {
      token,
      password,
    },
  });
  return resetPassword;
};

export const confirmEmail = async (onRequest: RequestSender, token: string) => {
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

  const { confirmEmail } = await onRequest(mutation, {
    token,
  });
  return confirmEmail;
};

export const getMe = async (onRequest: RequestSender) => {
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

export const updateMe = async (onRequest: RequestSender, fullName: string) => {
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

  const { updateMe } = await onRequest(mutation, {
    input: {
      fullName,
    },
  });
  return updateMe;
};

export const changeMyPassword = async (
  onRequest: RequestSender,
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

  const { changeMyPassword } = await onRequest(mutation, {
    input: {
      currentPassword,
      newPassword,
    },
  });
  return changeMyPassword;
};

export const deleteMe = async (onRequest: RequestSender) => {
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
