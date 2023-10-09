import { type Cookie } from '@builder.io/qwik-city';

export class ServerCookiesStorage {
  readonly cookie: Cookie;
  readonly lifetime: Date;
  readonly path: string;

  constructor(cookie: Cookie, lifetime: Date, path: string) {
    this.cookie = cookie;
    this.lifetime = lifetime;
    this.path = path;
  }

  get = (key: string) => {
    const cookieValue = this.cookie.get(key);
    return cookieValue?.value ?? null;
  };

  set = (key: string, value: string) => {
    this.cookie.set(key, value, { path: this.path, expires: this.lifetime });
  };

  remove = (key: string) => {
    this.cookie.delete(key, { path: this.path });
  };
}
