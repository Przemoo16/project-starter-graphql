export const getApiURL = (isServer: boolean): string => {
  const serverApiURL =
    import.meta.env.VITE_SERVER_API_URL ?? 'http://proxy/graphql';
  const clientApiURL =
    import.meta.env.VITE_CLIENT_API_URL ?? 'http://localhost:5173/graphql';
  return isServer ? serverApiURL : clientApiURL;
};

export enum RouteURL {
  ConfirmEmail = '/confirm-email',
  Dashboard = '/dashboard',
  Home = '/',
  Login = '/login',
  RecoverPassword = '/recover-password',
  Register = '/register',
  ResetPassword = '/reset-password',
}
