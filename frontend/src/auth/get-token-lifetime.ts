const TOKEN_LIFETIME_DAYS = 7; // Some browsers cap client-side cookies to 7 days of storage

export const getTokenLifetime = () => {
  const date = new Date();
  date.setDate(date.getDate() + TOKEN_LIFETIME_DAYS);
  return date;
};
