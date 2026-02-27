import json

try:
    import azure.functions as func
except ImportError:  # pragma: no cover
    func = None

from mcp_server.tools.canvas_tools_handler import CanvasToolsHandler

handler = CanvasToolsHandler()


def _handle_request(payload: dict) -> dict:
    tool_name = payload.get("tool")
    args = payload.get("arguments", {})
    if not tool_name:
        raise ValueError("Missing 'tool' in payload")
    result = handler.dispatch(str(tool_name), args)
    return {"ok": True, "result": result}


if func is not None:
    app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

    @app.route(route="mcp/tools", methods=["POST"])
    def mcp_tools(req: func.HttpRequest) -> func.HttpResponse:
        try:
            payload = req.get_json()
            result = _handle_request(payload)
            return func.HttpResponse(
                body=json.dumps(result), status_code=200, mimetype="application/json"
            )
        except Exception as exc:  # pragma: no cover
            return func.HttpResponse(
                body=json.dumps({"ok": False, "error": str(exc)}),
                status_code=400,
                mimetype="application/json",
            )
