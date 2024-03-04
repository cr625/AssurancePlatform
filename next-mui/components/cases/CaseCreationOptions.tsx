'use client'

import React, { useState, useCallback } from "react";
// import TemplateSelector from "./TemplateSelector.js";
import { useLoginToken } from "@/hooks/useAuth";
import { Button, Typography } from "@mui/material";
import { ColumnFlow, RowFlow } from "@/components/common/Layouts";
import TextInput from "@/components/common/TextInput";
// import LoadingSpinner from "./common/LoadingSpinner.jsx";
// import { ArrowRight } from "./common/Icons.jsx";
import ErrorMessage from "@/components/common/ErrorMessage";
import { useRouter } from "next/navigation";
import { ArrowRightIcon } from "lucide-react";
import TemplateSelector from "./TemplateSelector";

/**
 * Maximum allowed lengths for title and description,
 * see /eap_backend/eap_api/models.py
 */
const titleMaxLength = 200;
const descriptionMaxLength = 1000;


/**
 * CaseCreatorFlow component guides the user through the process of creating a new assurance case.
 * It consists of two stages: entering basic case details (title and description),
 * and selecting a template for the case. Upon completion, the case is posted to the server.
 *
 * @param {Object} props Component props.
 * @param {string} props.titleId A unique ID for the title element, used for accessibility.
 * @param {Function} props.onClose Function to call when the user chooses to close the modal.
 */

interface CaseCreatorOptionsProps {
  titleId: any,
  onClose: () => void
}

function CaseCreatorOptions({ titleId, onClose } : CaseCreatorOptionsProps) {
  const [stage, setStage] = useState(0);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [template, setTemplate] = useState("");
  const [titleError, setTitleError] = useState("");
  const [descriptionError, setDescriptionError] = useState("");
  const [templateError, setTemplateError] = useState("");
  const [errors, setErrors] = useState<string[]>([]);
  const [dirty0, setDirty0] = useState(false);
  const [dirty1, setDirty1] = useState(false);
  const [loading, setLoading] = useState(false);

  const router = useRouter()

  const [token] = useLoginToken();

  const postCaseJSON = useCallback(
    (json_str: string) => {
      const requestOptions: RequestInit = {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Token ${token}`,
        },
        body: json_str,
      };

      setLoading(true);

      fetch("http://localhost:8000/api/cases/", requestOptions)
        .then((response) => response.json())
        .then((json) => {
          if (json.id) {
            // navigate("/case/" + json.id);
            router.push(`/case/${json.id}`)
          } else {
            console.error(json);
            setLoading(false);
            setErrors(["An error occurred, please try again later"]);
          }
        })
        .catch((ex) => {
          console.error(ex);
          setLoading(false);
          setErrors(["An error occurred, please try again later"]);
        });
    },
    [token]
  );

  const onSubmit = useCallback(
    (e: any) => {
      e.preventDefault();
      if (stage === 0) {
        if (
          !title ||
          !description ||
          title.length >= titleMaxLength ||
          description.length >= descriptionMaxLength
        ) {
          setDirty0(true);
          return;
        }
        setStage(1);
      } else {
        // if (!template) {
        //   setDirty1(true);
        //   return;
        // }

        const case_json = JSON.parse(JSON.stringify(template));
        case_json["name"] = title;
        case_json["description"] = description;
        case_json["color_profile"] = "default";
        postCaseJSON(JSON.stringify(case_json));
      }
    },
    [stage, title, description, template, postCaseJSON]
  );

  const goBack = useCallback(() => {
    window.history.go(-1)
  }, []);

  return (
    <ColumnFlow component="form" onSubmit={onSubmit} noValidate>
      <Typography id={titleId} variant="h2" component="h3">
        {stage === 0 ? "Create a new assurance case" : "Pick a template"}
      </Typography>
      <ErrorMessage errors={errors}/>
      {stage === 0 ? (
        <>
          <TextInput
            label="Title"
            value={title}
            setValue={setTitle}
            error={titleError}
            setError={setTitleError}
            dirty={dirty0}
            required
            maxLength={titleMaxLength}
            placeholder="Assurance Case 1"
          />
          <TextInput
            multiline
            rows={2}
            label="Description"
            value={description}
            setValue={setDescription}
            error={descriptionError}
            setError={setDescriptionError}
            dirty={dirty0}
            required
            maxLength={descriptionMaxLength}
            placeholder="Write down a small description of what the case is intended for"
          />
        </>
      ) : (
        <>
          <TemplateSelector
            value={template}
            setValue={setTemplate}
            error={templateError}
            setError={setTemplateError}
            dirty={dirty1}
          />
        </>
      )}
      <RowFlow sx={{ marginTop: "auto" }}>
        {loading ? (
          // <LoadingSpinner />
          <p>Loading...</p>
        ) : stage === 0 ? (
          <>
            <Button
              onClick={onClose}
              variant="outlined"
              sx={{ marginLeft: "auto" }}
            >
              Cancel
            </Button>
            <Button type="submit" endIcon={<ArrowRightIcon />}>Continue</Button>
          </>
        ) : (
          <>
            <Button onClick={goBack} variant="text">
              Back
            </Button>
            <Button
              onClick={onClose}
              variant="outlined"
              sx={{ marginLeft: "auto" }}
            >
              Cancel
            </Button>
            <Button type="submit"  endIcon={<ArrowRightIcon />}>Create</Button>
          </>
        )}
      </RowFlow>
    </ColumnFlow>
  );
}

export default CaseCreatorOptions;
