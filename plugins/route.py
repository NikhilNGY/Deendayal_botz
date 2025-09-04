import re
import math
import logging
import secrets
import mimetypes
from aiohttp import web
from aiohttp.http_exceptions import BadStatusLine

from Deendayal_botz.Bot import multi_clients, work_loads
from Deendayal_botz.server.exceptions import FIleNotFound, InvalidHash
from Deendayal_botz.util.custom_dl import ByteStreamer
from Deendayal_botz.util.render_template import render_page
from info import MULTI_CLIENT

# -------------------------------
# ROUTES
# -------------------------------
routes = web.RouteTableDef()


@routes.get("/", allow_head=True)
async def root_route_handler(request: web.Request):
    """Root endpoint just to verify server is running."""
    return web.json_response({"status": "Deendayal_Botz server running"})


@routes.get(r"/watch/{path:\S+}", allow_head=True)
async def watch_handler(request: web.Request):
    """Serve HTML watch page."""
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            msg_id = int(match.group(2))
        else:
            msg_id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")

        html_page = await render_page(msg_id, secure_hash)
        return web.Response(text=html_page, content_type="text/html")

    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        raise web.HTTPBadRequest(text="Invalid request")
    except Exception as e:
        logging.exception("Unhandled error in watch_handler", exc_info=True)
        raise web.HTTPInternalServerError(text=str(e))


@routes.get(r"/{path:\S+}", allow_head=True)
async def download_handler(request: web.Request):
    """Serve actual media file with streaming support."""
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            msg_id = int(match.group(2))
        else:
            msg_id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")

        return await media_streamer(request, msg_id, secure_hash)

    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        raise web.HTTPBadRequest(text="Invalid request")
    except Exception as e:
        logging.exception("Unhandled error in download_handler", exc_info=True)
        raise web.HTTPInternalServerError(text=str(e))


# -------------------------------
# MEDIA STREAMER
# -------------------------------
class_cache = {}


async def media_streamer(request: web.Request, msg_id: int, secure_hash: str):
    """Stream Telegram files through aiohttp with Range support."""

    # Get Range header
    range_header = request.headers.get("Range", None)

    # Pick least loaded client
    index = min(work_loads, key=work_loads.get)
    faster_client = multi_clients[index]

    if MULTI_CLIENT:
        logging.info(f"Client {index} serving request from {request.remote}")

    # Reuse ByteStreamer object per client
    if faster_client not in class_cache:
        logging.debug(f"Creating ByteStreamer for client {index}")
        class_cache[faster_client] = ByteStreamer(faster_client)

    tg_connect = class_cache[faster_client]

    # Fetch file info
    file_id = await tg_connect.get_file_properties(msg_id)
    if not file_id:
        raise FIleNotFound("File not found in Telegram servers")

    if file_id.unique_id[:6] != secure_hash:
        logging.warning(f"Invalid hash for message {msg_id}")
        raise InvalidHash("File hash mismatch")

    file_size = file_id.file_size

    # Range parsing
    if range_header:
        from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
        from_bytes = int(from_bytes)
        until_bytes = int(until_bytes) if until_bytes else file_size - 1
    else:
        from_bytes = request.http_range.start or 0
        until_bytes = (request.http_range.stop or file_size) - 1

    if until_bytes >= file_size or from_bytes < 0 or until_bytes < from_bytes:
        return web.Response(
            status=416,
            text="416: Range Not Satisfiable",
            headers={"Content-Range": f"bytes */{file_size}"},
        )

    # Chunk setup
    chunk_size = 1024 * 1024
    until_bytes = min(until_bytes, file_size - 1)

    offset = from_bytes - (from_bytes % chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = until_bytes % chunk_size + 1

    req_length = until_bytes - from_bytes + 1
    part_count = math.ceil(until_bytes / chunk_size) - math.floor(offset / chunk_size)

    body = tg_connect.yield_file(
        file_id, index, offset, first_part_cut, last_part_cut, part_count, chunk_size
    )

    # File metadata
    file_name = file_id.file_name or f"{secrets.token_hex(2)}.bin"
    mime_type = file_id.mime_type or mimetypes.guess_type(file_name)[0] or "application/octet-stream"

    return web.Response(
        status=206 if range_header else 200,
        body=body,
        headers={
            "Content-Type": mime_type,
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Length": str(req_length),
            "Content-Disposition": f'attachment; filename="{file_name}"',
            "Accept-Ranges": "bytes",
        },
    )