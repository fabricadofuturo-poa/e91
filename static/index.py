"""Contador"""

import logging
logging.basicConfig(level = logging.INFO)
# ~ logging.basicConfig(level = logging.DEBUG)
logger = logging.getLogger(__name__)

try:
  import asyncio
  from datetime import datetime, timedelta
  import js
  from js import document
  import pyodide
  from pyodide import http
  from pyodide import create_proxy
  import time
except Exception as e:
  logger.exception(e)

async def reinicia_contador(*args, **kwargs) -> None:
  """Atualiza contador com o dos Guri"""
  try:
    global hora_fim
    api_response: object = await http.pyfetch(contador_url)
    if api_response.status:
      response: dict[str] = await api_response.json()
      hora_fim = datetime.fromtimestamp(
        float(response.get("date")))
  except Exception as e:
    # ~ logger.exception(e)
    # ~ display_error(e)
    pass

def atualiza_contador(*args, **kwargs) -> None:
  """Atualiza o contador a cada segundo"""
  try:
    global hora_fim
    diferença: timedelta = hora_fim - datetime.now()
    for item in (ch, cm, cs):
      item.innerText = ""
    if diferença.total_seconds() > 0.0:
      contador.element.classList.remove("bg-warning")
      contador.element.classList.add("bg-success")
      minutos, segundos = divmod(diferença.total_seconds(), 60)
      horas = divmod(minutos, 60)[0]
      if horas > 0.0:
        ch.innerText = f"{horas:02.0f} :"
      if minutos > 0.0:
        cm.innerText = f"{minutos:02.0f} :"
      if segundos > 0.0:
        cs.innerText = f"{segundos:02.0f}"
    else:
      contador.element.classList.remove("bg-success")
      contador.element.classList.add("bg-warning")
      cm.innerText = "TERMINOU!"
  except Exception as e:
    # ~ logger.exception(e)
    pass

try:
  hora_fim: datetime = datetime.now()
  contador: Element = Element("contador");
  contador.innerText = "";
  ch: Element = document.createElement("div");
  cm: Element = document.createElement("div");
  cs: Element = document.createElement("div");
  for item in (ch, cm, cs):
    for _class in ("col", "fs-1", "text-light"):
      item.classList.add(_class)
    item.innerText = "00 :"
    contador.element.appendChild(item)
  cs.innerText = "00"
  proxy: object = create_proxy(atualiza_contador)
  proxy3: object = create_proxy(reinicia_contador)
  interval1: int = js.setInterval(proxy, 1000)
  interval3: int = js.setInterval(proxy3, 10000)
except Exception as e:
  logger.exception(e)
