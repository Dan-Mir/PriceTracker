import axios from 'axios';

const API_URL = '/api';
const AUTH_TOKEN_KEY = 'authToken';

export const checkAuth = (): boolean => {
  return sessionStorage.getItem(AUTH_TOKEN_KEY) !== null;
};

export const login = async (username: string, password: string): Promise<boolean> => {
  try {
    const response = await axios.post(`${API_URL}/auth/login`, { username, password });
    if (response.data.token) {
      sessionStorage.setItem(AUTH_TOKEN_KEY, response.data.token);
      return true;
    }
    return false;
  } catch (error) {
    console.error('Login failed', error);
    return false;
  }
};

export const register = async (username: string, password: string): Promise<boolean> => {
    try {
        await axios.post(`${API_URL}/auth/register`, { username, password });
        return true;
    } catch (error) {
        console.error('Registration failed', error);
        return false;
    }
};

export const logout = (): void => {
  sessionStorage.removeItem(AUTH_TOKEN_KEY);
};

export const getAuthToken = (): string | null => {
    return sessionStorage.getItem(AUTH_TOKEN_KEY);
}
