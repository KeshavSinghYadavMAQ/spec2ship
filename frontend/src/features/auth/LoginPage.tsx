import { useState } from "react";
import { Body1, Button, Field, Input, makeStyles, tokens } from "@fluentui/react-components";
import { useLocation, useNavigate } from "react-router-dom";

import { ApiError } from "../../services/apiClient";
import { authClient } from "../../services/authClient";

const useStyles = makeStyles({
  container: {
    display: "grid",
    gap: tokens.spacingVerticalM,
    maxWidth: "28rem",
  },
});

export function LoginPage() {
  const styles = useStyles();
  const navigate = useNavigate();
  const location = useLocation();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      await authClient.login({ identifier, password });
      const redirectPath = (location.state as { from?: string } | null)?.from ?? "/inventory";
      navigate(redirectPath, { replace: true });
    } catch (error) {
      if (error instanceof ApiError && error.status === 423) {
        setErrorMessage("Your account is temporarily locked. Try again later.");
      } else {
        setErrorMessage("Invalid credentials. Please try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className={styles.container} aria-label="Login page scaffold">
      <Body1>Sign in to continue.</Body1>
      <form className={styles.container} onSubmit={handleSubmit}>
        <Field label="Identifier">
          <Input
            name="identifier"
            autoComplete="username"
            value={identifier}
            onChange={(_, data) => setIdentifier(data.value)}
          />
        </Field>
        <Field label="Password">
          <Input
            name="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(_, data) => setPassword(data.value)}
          />
        </Field>
        {errorMessage ? <Body1>{errorMessage}</Body1> : null}
        <Button appearance="primary" type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Signing in..." : "Sign in"}
        </Button>
      </form>
    </section>
  );
}
