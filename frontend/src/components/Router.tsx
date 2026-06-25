import { MemberProvider } from '@/integrations';
import { createBrowserRouter, RouterProvider, Navigate, Outlet, useLocation } from 'react-router-dom';
import { ScrollToTop } from '@/lib/scroll-to-top';
import ErrorPage from '@/integrations/errorHandlers/ErrorPage';
import { MemberProtectedRoute } from '@/components/ui/member-protected-route';
import { AnimatePresence, motion } from 'framer-motion';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

// Pages
import HomePage from '@/components/pages/HomePage';
import FeaturesPage from '@/components/pages/FeaturesPage';
import PracticePage from '@/components/pages/PracticePage';
import SessionDetailPage from '@/components/pages/SessionDetailPage';
import DashboardPage from '@/components/pages/DashboardPage';
import ProgressPage from '@/components/pages/ProgressPage';
import ResourcesPage from '@/components/pages/ResourcesPage';
import ResourceDetailPage from '@/components/pages/ResourceDetailPage';
import AboutPage from '@/components/pages/AboutPage';
import ContactPage from '@/components/pages/ContactPage';
import ProfilePage from '@/components/pages/ProfilePage';
import LoginPage from '@/components/pages/LoginPage';
import RegisterPage from '@/components/pages/RegisterPage';
import PrivacyPage from '@/components/pages/PrivacyPage';
import TermsPage from '@/components/pages/TermsPage';
import VerifyEmailPage from '@/components/pages/VerifyEmailPage';
import ForgotPasswordPage from '@/components/pages/ForgotPasswordPage';
import OAuthCallbackPage from '@/components/pages/OAuthCallbackPage';
import LiveSessionPage from '@/components/pages/LiveSessionPage';
import RecruiterDashboardPage from '@/components/pages/RecruiterDashboardPage';
import PlaybackPage from '@/components/pages/PlaybackPage';
import ComparePage from '@/components/pages/ComparePage';

// Page transition variants
const pageVariants: any = {
  initial: {
    opacity: 0,
    y: 20,
    scale: 0.99,
  },
  animate: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: "easeOut",
    },
  },
  exit: {
    opacity: 0,
    y: -15,
    scale: 0.99,
    transition: {
      duration: 0.3,
      ease: "easeOut",
    },
  },
};

// Animated page wrapper component
function AnimatedPage({ children }: { children: React.ReactNode }) {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={location.pathname}
        variants={pageVariants}
        initial="initial"
        animate="animate"
        exit="exit"
        className="w-full min-h-screen"
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}

// Layout component that includes ScrollToTop and page transitions
function Layout() {
  const location = useLocation();

  return (
    <>
      <ScrollToTop />
      <AnimatePresence mode="wait">
        <motion.div
          key={location.pathname}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -15 }}
          transition={{
            duration: 0.5,
            ease: [0.25, 0.46, 0.45, 0.94]
          }}
          className="w-full"
        >
          <Outlet />
        </motion.div>
      </AnimatePresence>
    </>
  );
}

const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    errorElement: <ErrorPage />,
    children: [
      {
        index: true,
        element: <HomePage />,
        routeMetadata: {
          pageIdentifier: 'home',
        },
      },
      {
        path: "features",
        element: <FeaturesPage />,
      },
      {
        path: "practice",
        element: (
          <MemberProtectedRoute messageToSignIn="Sign in to start practicing interviews">
            <PracticePage />
          </MemberProtectedRoute>
        ),
      },
      {
        path: "practice/new",
        element: (
          <MemberProtectedRoute messageToSignIn="Sign in to start a new practice session">
            <LiveSessionPage />
          </MemberProtectedRoute>
        ),
      },
      {
        path: "demo",
        element: <LiveSessionPage />
      },
      {
        path: "practice/:id",
        element: (
          <MemberProtectedRoute messageToSignIn="Sign in to view session details">
            <SessionDetailPage />
          </MemberProtectedRoute>
        ),
      },
      {
        path: "dashboard",
        element: (
          <MemberProtectedRoute messageToSignIn="Sign in to access your dashboard" requiredRole="candidate">
            <DashboardPage />
          </MemberProtectedRoute>
        ),
      },
      {
        path: "recruiter",
        element: (
          <MemberProtectedRoute messageToSignIn="Sign in as recruiter" requiredRole="recruiter">
            <RecruiterDashboardPage />
          </MemberProtectedRoute>
        ),
      },
      {
        path: "reports/:sessionId/playback",
        element: (
          <MemberProtectedRoute messageToSignIn="Sign in to view playback">
            <PlaybackPage />
          </MemberProtectedRoute>
        ),
      },
      {
        path: "reports/:sessionId/compare",
        element: (
          <MemberProtectedRoute messageToSignIn="Sign in to compare">
            <ComparePage />
          </MemberProtectedRoute>
        ),
      },
      {
        path: "progress",
        element: (
          <MemberProtectedRoute messageToSignIn="Sign in to view your progress">
            <ProgressPage />
          </MemberProtectedRoute>
        ),
      },
      {
        path: "resources",
        element: <ResourcesPage />,
      },
      {
        path: "resources/:id",
        element: <ResourceDetailPage />,
      },
      {
        path: "about",
        element: <AboutPage />,
      },
      {
        path: "contact",
        element: <ContactPage />,
      },
      {
        path: "profile",
        element: (
          <MemberProtectedRoute>
            <ProfilePage />
          </MemberProtectedRoute>
        ),
      },
      {
        path: "login",
        element: <LoginPage />,
      },
      {
        path: "register",
        element: <RegisterPage />,
      },
      {
        path: "privacy",
        element: <PrivacyPage />,
      },
      {
        path: "terms",
        element: <TermsPage />,
      },
      {
        path: "verify-email",
        element: <VerifyEmailPage />,
      },
      {
        path: "forgot-password",
        element: <ForgotPasswordPage />,
      },
      {
        path: "auth/callback",
        element: <OAuthCallbackPage />,
      },
      {
        path: "*",
        element: <Navigate to="/" replace />,
      },
    ],
  },
], {
  basename: import.meta.env.BASE_NAME,
});

export default function AppRouter() {
  return (
    <QueryClientProvider client={queryClient}>
      <MemberProvider>
        <RouterProvider router={router} />
      </MemberProvider>
    </QueryClientProvider>
  );
}
