import { type Cookie } from '@builder.io/qwik-city';

import { type SameSite } from './types';

export class ServerCookiesStorage {
  readonly cookie: Cookie;
  readonly lifetime: Date;
  readonly path: string;
  readonly secure: boolean;
  readonly sameSite: SameSite;

  constructor(
    cookie: Cookie,
    lifetime: Date,
    path: string = '/',
    secure: boolean = true,
    sameSite: SameSite = 'lax',
  ) {
    this.cookie = cookie;
    this.lifetime = lifetime;
    this.path = path;
    this.secure = secure;
    this.sameSite = sameSite;
  }

  get = (key: string) => {
    const cookieValue = this.cookie.get(key);
    return cookieValue?.value ?? null;
  };

  set = (key: string, value: string) => {
    this.cookie.set(key, value, {
      path: this.path,
      expires: this.lifetime,
      secure: this.secure,
      sameSite: this.sameSite,
    });
  };

  remove = (key: string) => {
    this.cookie.delete(key, { path: this.path });
  };
}
