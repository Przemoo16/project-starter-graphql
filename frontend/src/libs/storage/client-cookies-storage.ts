import Cookies from 'js-cookie';

export class ClientCookiesStorage {
  readonly lifetime: Date;
  readonly path: string;

  constructor(lifetime: Date, path: string) {
    this.lifetime = lifetime;
    this.path = path;
  }

  get = (key: string) => Cookies.get(key) ?? null;

  set = (key: string, value: string) => {
    Cookies.set(key, value, { path: this.path, expires: this.lifetime });
  };

  remove = (key: string) => {
    Cookies.remove(key, { path: this.path });
  };
}
