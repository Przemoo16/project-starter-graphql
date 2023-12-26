export type Maybe<T> = T | null;
export type InputMaybe<T> = Maybe<T>;
export type Exact<T extends { [key: string]: unknown }> = {
  [K in keyof T]: T[K];
};
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & {
  [SubKey in K]?: Maybe<T[SubKey]>;
};
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & {
  [SubKey in K]: Maybe<T[SubKey]>;
};
export type MakeEmpty<
  T extends { [key: string]: unknown },
  K extends keyof T,
> = { [_ in K]?: never };
export type Incremental<T> =
  | T
  | {
      [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never;
    };
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string };
  String: { input: string; output: string };
  Boolean: { input: boolean; output: boolean };
  Int: { input: number; output: number };
  Float: { input: number; output: number };
  UUID: { input: any; output: any };
};

export type ChangeMyPasswordFailure = {
  __typename?: 'ChangeMyPasswordFailure';
  problems: Array<ChangeMyPasswordProblem>;
};

export type ChangeMyPasswordInput = {
  currentPassword: Scalars['String']['input'];
  newPassword: Scalars['String']['input'];
};

export type ChangeMyPasswordProblem =
  | InvalidInputProblem
  | InvalidPasswordProblem;

export type ChangeMyPasswordResponse =
  | ChangeMyPasswordFailure
  | ChangeMyPasswordSuccess;

export type ChangeMyPasswordSuccess = {
  __typename?: 'ChangeMyPasswordSuccess';
  message: Scalars['String']['output'];
};

export type ConfirmEmailFailure = {
  __typename?: 'ConfirmEmailFailure';
  problems: Array<ConfirmEmailProblem>;
};

export type ConfirmEmailProblem =
  | InvalidEmailConfirmationTokenProblem
  | UserEmailAlreadyConfirmedProblem;

export type ConfirmEmailResponse = ConfirmEmailFailure | ConfirmEmailSuccess;

export type ConfirmEmailSuccess = {
  __typename?: 'ConfirmEmailSuccess';
  message: Scalars['String']['output'];
};

export type CreateUserFailure = {
  __typename?: 'CreateUserFailure';
  problems: Array<CreateUserProblem>;
};

export type CreateUserProblem = InvalidInputProblem | UserAlreadyExistsProblem;

export type CreateUserResponse = CreateUserFailure | User;

export type DeleteMeResponse = {
  __typename?: 'DeleteMeResponse';
  message: Scalars['String']['output'];
};

export type InvalidCredentialsProblem = Problem & {
  __typename?: 'InvalidCredentialsProblem';
  message: Scalars['String']['output'];
};

export type InvalidEmailConfirmationTokenProblem = Problem & {
  __typename?: 'InvalidEmailConfirmationTokenProblem';
  message: Scalars['String']['output'];
};

export type InvalidInputProblem = Problem & {
  __typename?: 'InvalidInputProblem';
  message: Scalars['String']['output'];
  path: Array<Scalars['String']['output']>;
};

export type InvalidPasswordProblem = Problem & {
  __typename?: 'InvalidPasswordProblem';
  message: Scalars['String']['output'];
};

export type InvalidResetPasswordTokenProblem = Problem & {
  __typename?: 'InvalidResetPasswordTokenProblem';
  message: Scalars['String']['output'];
};

export type LoginFailure = {
  __typename?: 'LoginFailure';
  problems: Array<LoginProblem>;
};

export type LoginInput = {
  password: Scalars['String']['input'];
  username: Scalars['String']['input'];
};

export type LoginProblem =
  | InvalidCredentialsProblem
  | UserEmailNotConfirmedProblem;

export type LoginResponse = LoginFailure | LoginSuccess;

export type LoginSuccess = {
  __typename?: 'LoginSuccess';
  accessToken: Scalars['String']['output'];
  refreshToken: Scalars['String']['output'];
  tokenType: Scalars['String']['output'];
};

export type Mutation = {
  __typename?: 'Mutation';
  changeMyPassword: ChangeMyPasswordResponse;
  confirmEmail: ConfirmEmailResponse;
  createUser: CreateUserResponse;
  deleteMe: DeleteMeResponse;
  login: LoginResponse;
  recoverPassword: RecoverPasswordResponse;
  refreshToken: RefreshTokenResponse;
  resetPassword: ResetPasswordResponse;
  updateMe: UpdateMeResponse;
};

export type MutationChangeMyPasswordArgs = {
  input: ChangeMyPasswordInput;
};

export type MutationConfirmEmailArgs = {
  token: Scalars['String']['input'];
};

export type MutationCreateUserArgs = {
  input: UserCreateInput;
};

export type MutationLoginArgs = {
  input: LoginInput;
};

export type MutationRecoverPasswordArgs = {
  email: Scalars['String']['input'];
};

export type MutationRefreshTokenArgs = {
  token: Scalars['String']['input'];
};

export type MutationResetPasswordArgs = {
  input: ResetPasswordInput;
};

export type MutationUpdateMeArgs = {
  input: UpdateMeInput;
};

export type Problem = {
  message: Scalars['String']['output'];
};

export type Query = {
  __typename?: 'Query';
  me: User;
};

export type RecoverPasswordResponse = {
  __typename?: 'RecoverPasswordResponse';
  message: Scalars['String']['output'];
};

export type RefreshTokenResponse = {
  __typename?: 'RefreshTokenResponse';
  accessToken: Scalars['String']['output'];
  tokenType: Scalars['String']['output'];
};

export type ResetPasswordFailure = {
  __typename?: 'ResetPasswordFailure';
  problems: Array<ResetPasswordProblem>;
};

export type ResetPasswordInput = {
  password: Scalars['String']['input'];
  token: Scalars['String']['input'];
};

export type ResetPasswordProblem =
  | InvalidInputProblem
  | InvalidResetPasswordTokenProblem;

export type ResetPasswordResponse = ResetPasswordFailure | ResetPasswordSuccess;

export type ResetPasswordSuccess = {
  __typename?: 'ResetPasswordSuccess';
  message: Scalars['String']['output'];
};

export type UpdateMeFailure = {
  __typename?: 'UpdateMeFailure';
  problems: Array<InvalidInputProblem>;
};

export type UpdateMeInput = {
  fullName?: InputMaybe<Scalars['String']['input']>;
};

export type UpdateMeResponse = UpdateMeFailure | User;

export type User = {
  __typename?: 'User';
  email: Scalars['String']['output'];
  fullName: Scalars['String']['output'];
  id: Scalars['UUID']['output'];
};

export type UserAlreadyExistsProblem = Problem & {
  __typename?: 'UserAlreadyExistsProblem';
  message: Scalars['String']['output'];
};

export type UserCreateInput = {
  email: Scalars['String']['input'];
  fullName: Scalars['String']['input'];
  password: Scalars['String']['input'];
};

export type UserEmailAlreadyConfirmedProblem = Problem & {
  __typename?: 'UserEmailAlreadyConfirmedProblem';
  message: Scalars['String']['output'];
};

export type UserEmailNotConfirmedProblem = Problem & {
  __typename?: 'UserEmailNotConfirmedProblem';
  message: Scalars['String']['output'];
};
