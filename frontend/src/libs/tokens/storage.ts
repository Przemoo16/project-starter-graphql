import { type Cookie } from '@builder.io/qwik-city';
import Cookies from 'js-cookie';

export interface TokenStorage {
  get: (key: string) => string | null;
  set: (key: string, value: string) => void;
  remove: (key: string) => void;
}

export class ClientCookiesTokenStorage {
  lifetime: Date;

  constructor(lifetime: Date) {
    this.lifetime = lifetime;
  }

  get = (key: string) => Cookies.get(key) ?? null;

  set = (key: string, value: string) => {
    Cookies.set(key, value, { path: '/', expires: this.lifetime });
  };

  remove = (key: string) => {
    Cookies.remove(key);
  };
}

export class ServerCookiesTokenStorage {
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
