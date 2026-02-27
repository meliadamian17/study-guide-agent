"""OpenAI-compatible tool definitions used by the model orchestrator."""


def get_openai_tool_definitions() -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": "list_my_courses",
                "description": "List active student courses.",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_modules",
                "description": "List modules in a course.",
                "parameters": {
                    "type": "object",
                    "properties": {"course_id": {"type": "string"}},
                    "required": ["course_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_module_items",
                "description": "List items in a module.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "course_id": {"type": "string"},
                        "module_id": {"type": "string"},
                    },
                    "required": ["course_id", "module_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_page_content",
                "description": "Read Canvas page content.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "course_id": {"type": "string"},
                        "page_url": {"type": "string"},
                    },
                    "required": ["course_id", "page_url"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_file_content",
                "description": "Read Canvas file content by file ID.",
                "parameters": {
                    "type": "object",
                    "properties": {"file_id": {"type": "string"}},
                    "required": ["file_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_announcements",
                "description": "List announcements for context codes.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "context_codes": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["context_codes"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_assignments",
                "description": "List assignments for a course.",
                "parameters": {
                    "type": "object",
                    "properties": {"course_id": {"type": "string"}},
                    "required": ["course_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "write_study_guide",
                "description": "Write generated study guide output for a course.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "course_id": {"type": "string"},
                        "slug": {"type": "string"},
                        "content": {"type": "string"},
                        "meta": {"type": "object"},
                    },
                    "required": ["course_id", "content"],
                },
            },
        },
    ]
