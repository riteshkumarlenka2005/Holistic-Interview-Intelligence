import { useRouteError, isRouteErrorResponse, Link } from 'react-router-dom';

export default function ErrorPage() {
  const error = useRouteError();

  let errorMessage: string;
  let statusCode: number = 500;

  if (isRouteErrorResponse(error)) {
    errorMessage = error.statusText || error.data?.message || 'Page not found';
    statusCode = error.status;
  } else if (error instanceof Error) {
    errorMessage = error.message;
  } else if (typeof error === 'string') {
    errorMessage = error;
  } else {
    errorMessage = 'An unexpected error occurred';
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-6 p-8">
        <h1 className="text-6xl font-bold text-foreground">{statusCode}</h1>
        <h2 className="text-2xl font-semibold text-foreground">Oops! Something went wrong</h2>
        <p className="text-muted-foreground max-w-md mx-auto">{errorMessage}</p>
        <Link
          to="/"
          className="inline-flex items-center justify-center px-6 py-3 text-sm font-medium rounded-md bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          Go back home
        </Link>
      </div>
    </div>
  );
}
