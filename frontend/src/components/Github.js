import React, { useState, useEffect } from "react";
import {
  Box,
  TextInput,
  List,
  Image,
  Button,
  Select,
  Grid,
  Text,
} from "grommet";
import { useNavigate } from "react-router-dom";
import { getSelfUser } from "./utils.js";

const normalizeData = (data) => {
  if (!data || typeof data !== "object") {
    return {
      name: "N/A",
      type: "N/A",
    };
  }
  return {
    ...data,
    name: data.name || "N/A",
    type: data.type || "N/A",
  };
};

const GitHub = () => {
  const [selectedOrg, setSelectedOrg] = useState({});
  const [organizations, setOrganizations] = useState([]);
  const [repositories, setRepositories] = useState([]);
  const [selectedRepoFiles, setSelectedRepoFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const navigate = useNavigate();
  const [inputValue, setInputValue] = useState("");
  const [currentPath, setCurrentPath] = useState("/");
  const [selectedRepoFullName, setSelectedRepoFullName] = useState("");

  useEffect(() => {
    const fetchInitialData = async () => {
      const userGithubHandle = await getSelfUser()["username"];
      setSelectedOrg({ login: userGithubHandle || "Your Profile" });
      const token = localStorage.getItem("access_token");

      if (token) {
        // Fetch user organizations
        const orgsResponse = await fetch("https://api.github.com/user/orgs", {
          headers: {
            Authorization: `token ${token}`,
          },
        });
        const orgs = await orgsResponse.json();
        setOrganizations(orgs);

        // Fetch user's own repos
        const reposResponse = await fetch("https://api.github.com/user/repos", {
          headers: {
            Authorization: `token ${token}`,
          },
        });
        const repos = await reposResponse.json();
        setRepositories(repos);
      }

      fetchSpecificRepo();

      setLoading(false);
    };

    fetchInitialData();
  }, []);

  const handleFileOrFolderClick = (item) => {
    // Normalize the item first
    const normalizedItem = normalizeData(item);

    if (!normalizedItem.type || !normalizedItem.name) {
      console.error("Invalid item:", normalizedItem);
      return;
    }

    if (normalizedItem.type === "dir") {
      const newPath =
        currentPath === "/"
          ? `/${normalizedItem.name}`
          : `${currentPath}/${normalizedItem.name}`;
      setCurrentPath(newPath);
      fetchRepoContentsByPath(newPath);
    } else {
      setSelectedFile(normalizedItem);
    }
  };

  const fetchSpecificRepo = async () => {
    try {
      const repoURL =
        "https://api.github.com/repos/alan-turing-institute/AssurancePlatform";
      const response = await fetch(repoURL);
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const repo = await response.json();
      setRepositories((prevRepos) => [...prevRepos, repo]);
    } catch (error) {
      console.error("Error fetching specific repo:", error);
    }
  };

  const handleAddInput = () => {
    if (isRepositoryURL(inputValue)) {
      const matches = inputValue.match(
        /https:\/\/github\.com\/([a-zA-Z0-9_-]+)\/([a-zA-Z0-9_-]+)/,
      );
      const username = matches[1];
      const repoName = matches[2];
      fetchSingleRepo(username, repoName);
    } else {
      fetchUserRepos(inputValue);
      setSelectedOrg({ login: inputValue });
    }
    setInputValue("");
  };

  const handleOrgChange = ({ option }) => {
    setSelectedOrg(option);
    if (option) {
      fetchReposForOrg(option.login);
    }
  };

  const isRepositoryURL = (value) => {
    const regex = /https:\/\/github\.com\/([a-zA-Z0-9_-]+)\/([a-zA-Z0-9_-]+)/;
    return regex.test(value);
  };

  const fetchSingleRepo = (username, repoName) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      fetch(`https://api.github.com/repos/${username}/${repoName}`, {
        headers: {
          Authorization: `token ${token}`,
        },
      })
        .then((response) => response.json())
        .then((repo) => {
          setRepositories((prevRepos) => [...prevRepos, repo]);
        });
    }
  };

  const fetchUserRepos = (username) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      fetch(`https://api.github.com/users/${username}/repos`, {
        headers: {
          Authorization: `token ${token}`,
        },
      })
        .then((response) => response.json())
        .then((repos) => {
          setRepositories(repos);
        });
    }
  };

  const fetchReposForOrg = (orgLogin) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      fetch(`https://api.github.com/orgs/${orgLogin}/repos`, {
        headers: {
          Authorization: `token ${token}`,
        },
      })
        .then((response) => response.json())
        .then((repos) => {
          // Filter by permissions
          const filteredRepos = repos.filter(
            (repo) => repo.permissions.admin || repo.permissions.maintain,
          );
          setRepositories(filteredRepos);
        });
    }
  };

  const handleRepoClick = (repoName) => {
    setSelectedRepoFullName(repoName);
    const token = localStorage.getItem("access_token");
    if (token) {
      fetch(`https://api.github.com/repos/${repoName}/contents`, {
        headers: {
          Authorization: `token ${token}`,
        },
      })
        .then((response) => response.json())
        .then((files) => {
          setSelectedRepoFiles(files);
        })
        .catch((error) => {
          console.error("Error fetching repo files:", error);
        });
    }
  };

  const fetchRepoContentsByPath = (path) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      fetch(
        `https://api.github.com/repos/${selectedRepoFullName}/contents${path}`,
        {
          headers: {
            Authorization: `token ${token}`,
          },
        },
      )
        .then((response) => response.json())
        .then((contents) => {
          console.log("Selected Repo Files:", selectedRepoFiles);
          if (Array.isArray(contents)) {
            setSelectedRepoFiles(contents);
          } else if (
            contents &&
            typeof contents === "object" &&
            contents.name
          ) {
            // Checks if it's a single file object
            setSelectedRepoFiles([contents]); // Convert the single file object into an array
          } else {
            console.warn("The folder is empty or there's an error:", contents);
            setSelectedRepoFiles([]); // set to an empty array
          }
        })
        .catch((error) => {
          console.error("Error fetching repo contents by path:", error);
        });
    }
  };

  const handleGoUp = () => {
    const pathSegments = currentPath
      .split("/")
      .filter((segment) => segment.trim() !== "");
    pathSegments.pop();
    const newPath =
      pathSegments.length === 0 ? "/" : `/${pathSegments.join("/")}`;
    setCurrentPath(newPath);
    fetchRepoContentsByPath(newPath);
  };

  const handleImportClick = async () => {
    try {
      const response = await fetch(selectedFile.download_url);
      const fileContent = await response.text();
      navigate("/case/new", { state: { fileContent } });
    } catch (error) {
      console.error("Error fetching file content:", error);
    }
  };

  if (loading) {
    return <Box pad="medium">Loading repositories...</Box>;
  }

  const filteredRepos = repositories.filter((repo) =>
    repo.name.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  return (
    <Box pad="medium">
      <Grid columns={["flex", "flex", "flex"]} gap="medium">
        <Box>
          <Box direction="row" gap="small">
            <TextInput
              placeholder="GitHub Username or Repository URL"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
            />
            <Button label="Add" onClick={handleAddInput} />
          </Box>
          <Select
            placeholder="Select organization or user"
            options={[{ login: selectedOrg.login }, ...organizations]}
            labelKey="login"
            valueKey="login"
            onChange={handleOrgChange}
            value={selectedOrg && selectedOrg.login}
          />
          <TextInput
            placeholder="Search Repositories..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <Box height="medium" overflow="auto">
            <List
              data={filteredRepos}
              primaryKey="name"
              onClickItem={({ item }) => handleRepoClick(item.full_name)}
            />
          </Box>
        </Box>

        <Box height="medium">
          {currentPath !== "/" && (
            <Box
              direction="row"
              align="center"
              gap="small"
              margin={{ bottom: "small" }}
            >
              <Button label=".. go up" onClick={handleGoUp} />
              <Text>{currentPath}</Text>
            </Box>
          )}

          <Box overflow="auto" flex={true}>
            <List
              data={selectedRepoFiles}
              primaryKey="name"
              onClickItem={({ item }) => handleFileOrFolderClick(item)}
            />
          </Box>
        </Box>

        <Box>
          {selectedFile && (
            <Box>
              {selectedFile.name.endsWith(".svg") && (
                <Image src={selectedFile.download_url} />
              )}
              {(selectedFile.name.endsWith(".json") ||
                selectedFile.name.endsWith(".svg")) && (
                <Button label="Import as Case" onClick={handleImportClick} />
              )}
            </Box>
          )}
        </Box>
      </Grid>
    </Box>
  );
};

export default GitHub;
