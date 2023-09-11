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
  return (await response.json()).data;
};

const getApiURL = (): string => {
  const serverApiURL =
    import.meta.env.VITE_SERVER_API_URL ?? 'http://proxy/graphql';
  const clientApiURL =
    import.meta.env.VITE_CLIENT_API_URL ?? 'http://localhost:5173/graphql';
  return isServer ? serverApiURL : clientApiURL;
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
): Promise<any> => {
  // TODO: Fix any type
  return await sendGraphQLrequest(REGISTER_MUTATION, {
    input: {
      fullName,
      email,
      password,
    },
  });
};

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
  return await sendGraphQLrequest(LOGIN_MUTATION, {
    input: {
      username: email,
      password,
    },
  });
};

const RECOVER_PASSWORD_MUTATION = `
  mutation RecoverPassword($email: String!) {
    recoverPassword(email: $email) {
      message
    }
  }
`;

export const recoverPassword = async (email: string): Promise<any> => {
  // TODO: Fix any type
  return await sendGraphQLrequest(RECOVER_PASSWORD_MUTATION, {
    email,
  });
};

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
): Promise<any> => {
  // TODO: Fix any type
  return await sendGraphQLrequest(RESET_PASSWORD_MUTATION, {
    input: {
      token,
      password,
    },
  });
};

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

export const confirmEmail = async (token: string): Promise<any> => {
  // TODO: Fix any type
  return await sendGraphQLrequest(CONFIRM_EMAIL_MUTATION, {
    token,
  });
};

const GET_ME_QUERY = `
  query GetMe {
    me {
      id
    }
  }
`;

export const getMe = async (): Promise<any> => {
  // TODO: Fix any type
  return await sendGraphQLrequest(GET_ME_QUERY, {});
};

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

export const updateMe = async (fullName: string): Promise<any> => {
  // TODO: Fix any type
  return await sendGraphQLrequest(UPDATE_ME_MUTATION, {
    input: {
      fullName,
    },
  });
};

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
): Promise<any> => {
  // TODO: Fix any type
  return await sendGraphQLrequest(CHANGE_MY_PASSWORD_MUTATION, {
    input: {
      currentPassword,
      newPassword,
    },
  });
};

const DELETE_ME_MUTATION = `
  mutation DeleteMe {
    deleteMe {
      message
    }
  }
`;

export const deleteMe = async (): Promise<any> => {
  // TODO: Fix any type
  return await sendGraphQLrequest(DELETE_ME_MUTATION, {});
};
