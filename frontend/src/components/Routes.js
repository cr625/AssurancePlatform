import React from "react";
import "../index.css";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Navigation from "./Navigation"; // Navigation now includes UserProfileDropdown
import Home from "./Home";
import Login from "./Login";
import Signup from "./Signup";
import CaseCreator from "./CaseCreator";
import CaseContainer from "./CaseContainer";
import WorkInProcessBanner from "./WorkInProcessBanner";
import Logout from "./Logout";
import Groups from "./Groups";
import Github from "./Github";
import { Box, Toolbar } from "@mui/material";

const AllRoutes = () => {
  return (
    <Router>
      <Navigation />
      <Box component="main" sx={{ minHeight: "100vh", height: "100%", display: "flex", flexDirection: "column", overflow: "hidden" }}>
        <Toolbar />
      <WorkInProcessBanner />
        <Routes>
          <Route exact path="/" element={<Home />} />
          <Route path="/case">
            <Route path=":caseSlug" element={<CaseContainer />} />
          </Route>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/logout" element={<Logout />} />
          <Route path="/groups" element={<Groups />} />
          <Route path="/github" element={<Github />} />
        </Routes>
      </Box>
    </Router>
  );
};

export default AllRoutes;
