// src/auth/authProvider.ts
import { API_V1_URL } from '../config/api';
import { Credentials } from '../types/auth';
import { UserIdentity } from '../types/user';

const safeFetch = async (input: RequestInfo | URL, init?: RequestInit, fallbackMessage = 'API indisponível. Tente novamente mais tarde.') => {
  try {
    return await fetch(input, init);
  } catch (error) {
    console.error('API indisponível ou inacessível', error);
    throw new Error(fallbackMessage);
  }
};

const authProvider = {
  login: async ({ username, password }: Credentials) => {
    const res = await safeFetch(`${API_V1_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ username, password }),
    });

    if (!res.ok) {
      throw new Error('Login failed');
    }

    return Promise.resolve();
  },

  logout: async () => {
    await safeFetch(`${API_V1_URL}/logout`, {
      method: 'POST',
      credentials: 'include',
    });
    return Promise.resolve();
  },
  checkAuth: async () => {
    const res = await safeFetch(`${API_V1_URL}/me`, {
      method: 'GET',
      credentials: 'include',
    });
    return res.ok ? Promise.resolve() : Promise.reject(new Error('API indisponível. Tente novamente mais tarde.'));
  },
  checkError: ({ status }: { status: number }) => {
    return status === 401 || status === 403 ? Promise.reject() : Promise.resolve();
  },
  getPermissions: () => Promise.resolve(),
  getIdentity: async (): Promise<UserIdentity> => {
    try {
      const res = await safeFetch(`${API_V1_URL}/me`, {
        method: 'GET',
        credentials: 'include',
      });

      if (!res.ok) {
        throw new Error('Failed to fetch identity');
      }

      const user = await res.json();
      const identity: UserIdentity = {
        id: user.id,
        username: user.username,
        email: user.email,
        firstName: user.first_name,
        lastName: user.last_name,
        fullName:
          user.full_name ??
          [user.first_name, user.last_name]
            .filter((part: string | undefined) => Boolean(part))
            .join(' '),
        bio: user.bio,
        avatarUrl: user.avatar_url,
        createdAt: user.created_at,
        updatedAt: user.updated_at,
      };

      return identity;
    } catch (error) {
      console.error('Unable to retrieve identity', error);
      throw new Error('Failed to fetch identity');
    }
  },
};

export default authProvider;
