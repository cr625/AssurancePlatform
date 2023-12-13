import React, { useState, useEffect, useCallback } from "react";

import AtiButton, { NavButton } from "./common/AtiButton";
import { getBaseURL } from "./utils.js";
import Github from "./GithubLogin";
import { Alert, Box, Typography } from "@mui/material";
import AtiTextField from "./common/AtiTextField";
import LoadingSpinner from "./common/LoadingSpinner";
import { ColumnFlow, ModalLikeLayout, RowFlow } from "./common/Layout";
import { useEnforceLogout, useLoginToken } from "../hooks/useAuth.js";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [usernameError, setUsernameError] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [errors, setErrors] = useState([]);
  const [dirty, setDirty] = useState(false);
  const [loading, setLoading] = useState(true);

  const isLoggedOut = useEnforceLogout();
  const [_, setToken] = useLoginToken();

  useEffect(() => {
    setLoading(!isLoggedOut);
  }, [isLoggedOut]);

  const onSubmit = useCallback(
    (e) => {
      e.preventDefault();

      if (!username || !password) {
        setDirty(true);
        return;
      }

      setErrors([]);
      setLoading(true);
      const user = {
        username: username,
        password: password,
      };

      fetch(`${getBaseURL()}/auth/login/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(user),
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.key) {
            setToken(data.key);
            window.location.replace("/");
          } else {
            setLoading(false);
            setPassword("");
            setToken(null);
            setErrors(["Cannot log in with provided credentials"]);
          }
        })
        .catch(() => {
          setLoading(false); // Also set loading to false when there is an error
          setErrors(["An error occurred, please try again later"]);
        });
    },
    [username, password, setToken]
  );

  return (
    <ModalLikeLayout>
      <form noValidate onSubmit={onSubmit}>
        <ColumnFlow>
          <Typography variant="h2" component="h1" sx={{ marginBottom: "1rem" }}>
            Login
          </Typography>
          <Box sx={{ marginBottom: "1rem" }}>
            <Typography>Not already registered?</Typography>
            <NavButton to="/signup" variant="outlined">
              Sign-up
            </NavButton>
          </Box>
          <AtiTextField
            label="Username"
            value={username}
            setValue={setUsername}
            error={usernameError}
            setError={setUsernameError}
            dirty={dirty}
            required
            noRequiredSymbol
            inputProps={{
              autoComplete: "username",
            }}
          />
          <AtiTextField
            label="Password"
            type="password"
            value={password}
            setValue={setPassword}
            error={passwordError}
            setError={setPasswordError}
            dirty={dirty}
            required
            noRequiredSymbol
            inputProps={{
              autoComplete: "current-password",
            }}
          />
          {errors.map((err) => (
            <Alert key={err} severity="error">
              {err}
            </Alert>
          ))}
          <RowFlow>
            {loading ? (
              <LoadingSpinner sx={{ margin: "auto" }} />
            ) : (
              <>
                <Github variant="outlined" setLoading={setLoading} />
                <AtiButton type="submit" sx={{ marginLeft: "auto" }}>
                  Login
                </AtiButton>
              </>
            )}
          </RowFlow>
        </ColumnFlow>
      </form>
    </ModalLikeLayout>
  );
};

export default Login;
