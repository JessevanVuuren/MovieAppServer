def send_response(success, status, error, payload):
    return { "success": success, "status": status, "error": error, "payload": payload }