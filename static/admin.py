"""Dashboard dos Guri"""

import logging
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

try:
  import asyncio
  import json
  import pyodide
  from pyodide import http
except Exception as e:
  logger.exception(e)

log_alert: Element = Element("logging")

async def log(element: Element, text: str, bg: str) -> None:
  """Muda o fundo de um elemento e escreve texto"""
  try:
    if bg:
      all_bg: list[str] = ['primary', 'secondary', 'success', 'danger', 
        'warning', 'info', 'light', 'dark']
      for background in [b for b in all_bg if b is not bg]:
        element.element.classList.remove(f"alert-{background}")
      element.element.classList.add(f"alert-{bg}")
    element.element.innerText = text
  except Exception as e:
    logger.exception(e)

async def edita_contador(
  chave: str = chave,
  hora: str = "0",
  minuto: str = "0",
  segundo: str = "0",
  *args,
  **kwargs,
) -> None:
  """Atualiza contador dos Guri"""
  try:
    global url
    body: dict[str, str] = {
      'chave': chave,
      'hora': hora,
      'minuto': minuto,
      'segundo': segundo,
    }
    request: object = await http.pyfetch(
      url,
      method = "POST",
      body = json.dumps(body),
    )
    message: str = f"""request: {request}, url: {url}, body: {body}"""
    background: str = "danger"
    if request.status:
      response: dict[str] = await request.json()
      message = response["message"]
      background = "success"
      if not response["status"]:
        message = f"{response['message']}: {response['exception']}"
        background = "warning"
    await log(log_alert, message, background)
  except Exception as e:
    logger.exception(e)
