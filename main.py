"""Site pra passar slides"""

from quart import abort, Quart
from quart import render_template
from jinja2 import TemplateNotFound
import logging

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
  app.run()
