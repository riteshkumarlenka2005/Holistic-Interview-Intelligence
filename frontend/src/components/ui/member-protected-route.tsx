import { ReactNode } from 'react';
import { useMember } from '@/integrations';
import { SignIn } from '@/components/ui/sign-in';
import { LoadingSpinner } from '@/components/ui/loading-spinner';

interface SignInProps {
  title?: string;
  message?: string;
  className?: string;
  cardClassName?: string;
  buttonClassName?: string;
  buttonText?: string;
}

interface LoadingSpinnerProps {
  message?: string;
  className?: string;
  spinnerClassName?: string;
}

interface MemberProtectedRouteProps {
  children: ReactNode;

  // Simple props for quick customization
  messageToSignIn?: string;
  messageToLoading?: string;
  requiredRole?: string;
  signInTitle?: string;
  signInClassName?: string;
  loadingClassName?: string;

  // Advanced prop objects for full customization
  signInProps?: Partial<SignInProps>;
  loadingSpinnerProps?: Partial<LoadingSpinnerProps>;
}

export function MemberProtectedRoute({
  children,
  messageToSignIn = "Please sign in to access this page.",
  messageToLoading = "Loading page...",
  signInTitle = "Sign In Required",
  signInClassName = "",
  loadingClassName = "",
  requiredRole,
  signInProps = {},
  loadingSpinnerProps = {}
}: MemberProtectedRouteProps) {
  const { member, isAuthenticated, isLoading } = useMember();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <LoadingSpinner
          message={messageToLoading}
          className={loadingClassName}
          {...loadingSpinnerProps}
        />
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <SignIn
          title={signInTitle}
          message={messageToSignIn}
          className={signInClassName}
          {...signInProps}
        />
      </div>
    );
  }

  if (requiredRole && member?.role !== requiredRole) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="text-center bg-white p-8 rounded-lg shadow-md max-w-md w-full border border-red-100">
          <h2 className="text-2xl font-bold text-red-600 mb-2">Access Denied</h2>
          <p className="text-gray-600 mb-6">You do not have permission to view this page. This page requires {requiredRole} privileges.</p>
          <a href="/" className="inline-block bg-primary text-white px-6 py-2 rounded-md hover:bg-primary/90 transition-colors">
            Return Home
          </a>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
