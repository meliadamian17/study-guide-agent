from study_guide_agent.tools.openai_schemas import get_openai_tool_definitions


def test_tool_definitions_include_required_tools():
    tools = get_openai_tool_definitions()
    names = {t["function"]["name"] for t in tools}
    assert "list_my_courses" in names
    assert "list_modules" in names
    assert "get_module_items" in names
    assert "get_page_content" in names
    assert "get_file_content" in names
    assert "list_announcements" in names
    assert "list_assignments" in names
    assert "write_study_guide" in names


def test_write_study_guide_has_required_params():
    tools = get_openai_tool_definitions()
    write_tool = next(t for t in tools if t["function"]["name"] == "write_study_guide")
    params = write_tool["function"]["parameters"]["properties"]
    assert "course_id" in params
    assert "content" in params
