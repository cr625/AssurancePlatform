import { Box, Button, TextArea, List, Form, FormField } from "grommet";
import React, { useState, useEffect, useRef } from "react";
import { useParams } from "react-router-dom";
import { getBaseURL } from "./utils.js";

function CommentSection() {
  const { assuranceCaseId } = useParams();
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState("");
  const inputRef = useRef(null);

  useEffect(() => {
    fetchComments();
  }, [assuranceCaseId]);

  const fetchComments = async () => {
    const url = `${getBaseURL()}/comments/${assuranceCaseId}/`;
    const requestOptions = {
      method: "GET",
      headers: {
        Authorization: `Token ${localStorage.getItem("token")}`,
      },
    };
    const response = await fetch(url, requestOptions);
    const data = await response.json();
    setComments(data);
  };

  const handleNewCommentChange = (event) => setNewComment(event.target.value);

  const handlePostComment = async () => {
    const url = `${getBaseURL()}/comments/${assuranceCaseId}/`; // POST endpoint for a new comment
    const requestOptions = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Token ${localStorage.getItem("token")}`,
      },
      body: JSON.stringify({ text: newComment }),
    };
    const response = await fetch(url, requestOptions);
    if (response.ok) {
      setNewComment("");
      fetchComments();
    }
  };

  return (
    <Box fill="vertical" overflow="auto" align="start" flex="grow">
      <Box flex={false} direction="row" align="center" justify="between">
        <TextArea
          placeholder="Write your comment here..."
          value={newComment}
          onChange={handleNewCommentChange}
        />
        <Button label="Post Comment" onClick={handlePostComment} />
      </Box>
      <List data={comments}>
        {(datum, index) => (
          <Box
            key={index}
            direction="row"
            align="center"
            justify="between"
            pad="small"
          >
            {/* Removed edit functionality for each comment item as the provided Django views do not handle updates */}
            <span>{datum.text}</span>
          </Box>
        )}
      </List>
    </Box>
  );
}

export default CommentSection;
