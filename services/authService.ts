const AUTH_KEY = 'isLoggedIn';

export const checkAuth = (): boolean => {
  return sessionStorage.getItem(AUTH_KEY) === 'true';
};

export const login = (password: string): boolean => {
  // In a real app, this would be a secure check.
  // For this demo, any non-empty password works.
  if (password) {
    sessionStorage.setItem(AUTH_KEY, 'true');
    return true;
  }
  return false;
};

export const logout = (): void => {
  sessionStorage.removeItem(AUTH_KEY);
};
