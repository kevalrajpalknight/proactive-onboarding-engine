def get_structured_output_parser(result) -> dict:
    """Returns a parser that extracts structured output from agent responses."""
    structured = result.get("structured_response")
    if structured is None:
        print("No structured_response returned:", result)
        return

    # Pydantic v2: model_dump(); v1: dict()
    data = (
        structured.model_dump()
        if hasattr(structured, "model_dump")
        else structured.dict()
    )

    return data
