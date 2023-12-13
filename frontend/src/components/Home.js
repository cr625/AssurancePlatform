import React, { useState, useEffect } from "react";
import mockup_diagram from "../images/mockup-diagram.png";
import { CardMedia, Container, Typography } from "@mui/material";
import ManageCases from "./ManageCases";
import { useLoginToken } from "../hooks/useAuth";

const Splash = () => {
  // TODO #302 make a nicer splash screen
  return (
    <Container
      sx={{
        display: "flex",
        flexDirection: "column",
        flexShrink: 1,
        overflow: "hidden",
      }}
    >
      <Typography variant="h1">Ethical Assurance Platform</Typography>
      <CardMedia
        sx={{
          flexShrink: 1,
          objectFit: "contain",
          width: "100%",
          height: "100%",
        }}
        component="img"
        image={mockup_diagram}
        alt="Ethical Assurance flowchart"
      />
    </Container>
  );
};

const Home = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const [token] = useLoginToken();

  useEffect(() => {
    setIsLoggedIn(token != null);
  }, [token]);

  return isLoggedIn ? <ManageCases /> : <Splash />;
};

export default Home;
