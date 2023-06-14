"""Site pra passar slides"""

import asyncio
from jinja2 import TemplateNotFound
import logging
from quart import abort, Quart
from quart import render_template
import sys
import uvicorn

logging.basicConfig(level = logging.INFO)
logger: logging.Logger = logging.getLogger(__name__)

internet_clicker_code: str = "caat"

internet_clicker_url: str = f"https://www.internetclicker.com?code={internet_clicker_code}&branding=false"
vmix_url: str = "https://advanced.vmixcall.com/"

app = Quart(__name__)

@app.route('/')
async def hello():
  try:
    return await render_template(
      'index.html',
      code = internet_clicker_code,
      ic_url = internet_clicker_url,
      v_url = vmix_url,
    )
  except TemplateNotFound:
    await abort(404)
  except Exception as e:
    logger.exception(e)

if __name__ == '__main__':
  # ~ app.run()
# ~ else:
  try:
    uvicorn.run(
      app,
      uds = "uvicorn.socket",
      forwarded_allow_ips = "*",
      proxy_headers = True,
      timeout_keep_alive = 0,
      log_level = "info",
    )
  except (
    OSError,
    NotImplementedError,
    asyncio.exceptions.CancelledError,
  ):
    uvicorn.run(
      app,
      host = "127.0.0.1",
      port = 15000,
      forwarded_allow_ips = "*",
      proxy_headers = True,
      timeout_keep_alive = 0,
      log_level = "info",
    )
  except Exception as e:
    logger.exception(e)
