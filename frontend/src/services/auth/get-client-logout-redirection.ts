import { RouteURL } from '~/libs/api/route-url';

export const getClientLogoutRedirection = () => () => {
  window.location.assign(RouteURL.Login);
};
