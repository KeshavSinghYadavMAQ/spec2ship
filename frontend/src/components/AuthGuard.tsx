import { Spinner } from "@fluentui/react-components";
import { useQuery } from "@tanstack/react-query";
import { Navigate, useLocation } from "react-router-dom";
import type { ReactNode } from "react";

import { ApiError } from "../services/apiClient";
import { authClient } from "../services/authClient";

type AuthGuardProps = {
  children: ReactNode;
};

export function AuthGuard({ children }: AuthGuardProps) {
  const location = useLocation();
  const sessionQuery = useQuery({
    queryKey: ["auth", "session"],
    queryFn: authClient.getSession,
    retry: false,
  });

  if (sessionQuery.isLoading) {
    return <Spinner label="Checking session" />;
  }

  if (sessionQuery.error instanceof ApiError) {
    // Transitional compatibility while auth endpoints are being implemented.
    if (sessionQuery.error.status === 404) {
      return <>{children}</>;
    }
    if (sessionQuery.error.status === 401 || sessionQuery.error.status === 423) {
      return <Navigate to="/login" replace state={{ from: location.pathname }} />;
    }
  }

  if (sessionQuery.isError) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return <>{children}</>;
}
