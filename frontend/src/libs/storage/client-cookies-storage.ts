import Cookies from 'js-cookie';

export class ClientCookiesStorage {
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
