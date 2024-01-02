export class TestStorage {
  readonly storage = new Map<string, string>();

  get = (key: string) => this.storage.get(key) ?? null;

  set = (key: string, value: string) => {
    this.storage.set(key, value);
  };

  remove = (key: string) => {
    this.storage.delete(key);
  };
}
