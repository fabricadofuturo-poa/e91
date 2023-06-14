"""Site pra passar slides"""

import asyncio
from configparser import ConfigParser, NoSectionError
import datetime
from jinja2 import TemplateNotFound
import logging
import os
from quart import abort, Quart
from quart import render_template
import sys
import time
import uvicorn

config_file: str = os.path.join("config.ini")
internet_clicker_url: str | None = None
vmix_url: str | None = None
internet_clicker_code: str | None = None
vmix_name: str | None = None
vmix_key: str | None = None
uvicorn_socket: str | None = None
uvicorn_host: str | None = None
uvicorn_port: str | None = None
log_level: str | None = None

try:
  config: ConfigParser = ConfigParser()
  config.read(config_file)
  internet_clicker_code = config["internet_clicker"]["code"]
  vmix_name = config["vmix"]["name"]
  vmix_key = config["vmix"]["key"]
  internet_clicker_code = config["internet_clicker"]["code"]
  data = time.mktime(
    datetime.datetime.fromtimestamp(int(config["contador"]["date"])
    ).timetuple()) * 1e3
  uvicorn_socket = config["uvicorn"]["socket"]
  uvicorn_host = config["uvicorn"]["host"]
  uvicorn_port = int(config["uvicorn"]["port"])
  log_level = config["uvicorn"]["log_level"]
  internet_clicker_url = f"""https://www.internetclicker.com?code=\
{internet_clicker_code}&branding=false"""
  vmix_url = f"""https://advanced.vmixcall.com/call.htm?Key={vmix_key}\
&Name={vmix_name}"""
except (Exception, NoSectionError) as e:
  logging.exception(e)
  sys.exit("Arquivo de configuração não existe ou tá errado")

logging.basicConfig(level = log_level.upper())
logger: logging.Logger = logging.getLogger(__name__)

app: Quart = Quart(__name__)

@app.route("/")
async def apresentacao():
  try:
    return await render_template(
      "index.html",
      code = internet_clicker_code,
      ic_url = internet_clicker_url,
      v_url = vmix_url,
      v_name = vmix_name,
      v_key = vmix_key,
      data = data,
    )
  except TemplateNotFound as e:
    logger.exception(e)
    await abort(404)
  except Exception as e:
    logger.exception(e)

if __name__ == '__main__':
  try:
    uvicorn.run(
      app,
      uds = uvicorn_socket,
      forwarded_allow_ips = "*",
      proxy_headers = True,
      timeout_keep_alive = 0,
      log_level = log_level.lower(),
    )
  except (
    OSError,
    NotImplementedError,
    asyncio.exceptions.CancelledError,
  ):
    uvicorn.run(
      app,
      host = uvicorn_host,
      port = uvicorn_port,
      forwarded_allow_ips = "*",
      proxy_headers = True,
      timeout_keep_alive = 0,
      log_level = log_level.lower(),
    )
  except Exception as e:
    logger.exception(e)
    app.run()
