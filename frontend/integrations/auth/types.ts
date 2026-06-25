export interface MemberProfile {
  nickname?: string;
  bio?: string;
}

export interface Member {
  id: string;
  email: string;
  firstName?: string;
  lastName?: string;
  avatar?: string;
  isVerified: boolean;
  oauthProvider: 'local' | 'google' | 'github';
  role?: string;
  createdAt: Date;
  updatedAt: Date;
  profile?: MemberProfile;
}

export interface MemberState {
  member: Member | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  pendingVerification: boolean;
  pendingEmail: string | null;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  password: string;
  firstName?: string;
  lastName?: string;
}

export interface OTPVerification {
  email: string;
  code: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthResponse {
  user: Member;
  tokens: TokenResponse;
}

export interface MemberActions {
  loadCurrentMember: () => Promise<void>;
  login: () => void;
  loginWithCredentials: (credentials: LoginCredentials) => Promise<boolean>;
  loginWithGoogle: () => void;
  loginWithGitHub: () => void;
  register: (credentials: RegisterCredentials) => Promise<boolean>;
  verifyOTP: (verification: OTPVerification) => Promise<boolean>;
  resendOTP: (email: string) => Promise<boolean>;
  forgotPassword: (email: string) => Promise<boolean>;
  resetPassword: (email: string, code: string, newPassword: string) => Promise<boolean>;
  logout: () => void;
  clearMember: () => void;
  clearError: () => void;
}

export interface MemberContextType extends MemberState {
  actions: MemberActions;
}
