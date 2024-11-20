export interface BaseUser {
  email: string;
  password: string;
}

export interface BaseUserSocial {
  social_id: string;
  email: string;
  password: string;
}

export type BaseUserEmail = {
  email: string;
};

export type ChangePassword = {
  token: string;
  password: string;
};

export type UserSocial = {
  social_id: string;
  email: string;
  id?: string;
  token?: string;
};

export type UserLogin = {
  id: string;
  email: string;
  token: string;
};

export type User = {
  id: string;
  email: string;
};
