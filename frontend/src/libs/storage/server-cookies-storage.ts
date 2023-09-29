import { type Cookie } from '@builder.io/qwik-city';

export class ServerCookiesStorage {
  cookie: Cookie;
  lifetime: Date;

  constructor(cookie: Cookie, lifetime: Date) {
    this.cookie = cookie;
    this.lifetime = lifetime;
  }

  get = (key: string) => {
    const cookieValue = this.cookie.get(key);
    return cookieValue?.value ?? null;
  };

  set = (key: string, value: string) => {
    this.cookie.set(key, value, { path: '/', expires: this.lifetime });
  };

  remove = (key: string) => {
    this.cookie.delete(key);
  };
}
