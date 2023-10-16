import Cookies from 'js-cookie';

import { type SameSite } from './types';

export class ClientCookiesStorage {
  readonly lifetime: Date;
  readonly path: string;
  readonly secure: boolean;
  readonly sameSite: SameSite;

  constructor(
    lifetime: Date,
    path: string = '/',
    secure: boolean = true,
    sameSite: SameSite = 'lax',
  ) {
    this.lifetime = lifetime;
    this.path = path;
    this.secure = secure;
    this.sameSite = sameSite;
  }

  get = (key: string) => Cookies.get(key) ?? null;

  set = (key: string, value: string) => {
    Cookies.set(key, value, {
      path: this.path,
      expires: this.lifetime,
      secure: this.secure,
      sameSite: this.sameSite,
    });
  };

  remove = (key: string) => {
    Cookies.remove(key, { path: this.path });
  };
}
