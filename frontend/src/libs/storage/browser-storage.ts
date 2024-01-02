export class BrowserStorage {
  readonly storage: Storage;

  constructor(storage: Storage) {
    this.storage = storage;
  }

  get = (key: string) => this.storage.getItem(key);

  set = (key: string, value: string) => {
    this.storage.setItem(key, value);
  };

  remove = (key: string) => {
    this.storage.removeItem(key);
  };
}
