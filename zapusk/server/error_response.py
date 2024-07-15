import json
from flask import Response


def error_response(error: str, status: int):
    return Response(
        json.dumps({"error": error}),
        status=status,
    )
