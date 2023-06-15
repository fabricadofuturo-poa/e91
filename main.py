"""
call.fabricadofuturo.com

Copyright 2023 Fábrica do Futuro

Licensed under the Apache License, Version 2.0 (the "License"); you may 
not use this file except in compliance with the License. You may obtain 
a copy of the License at  

http://www.apache.org/licenses/LICENSE-2.0  

Unless required by applicable law or agreed to in writing, software 
distributed under the License is distributed on an "AS IS" BASIS, 
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or 
implied.  
See the License for the specific language governing permissions and 
limitations under the License.  
"""

import logging
import sys

try:
  from quart import (
    abort,
    # ~ current_app,
    flash,
    flask_patch,
    jsonify,
    Quart,
    render_template,
    render_template_string,
    request,
  )
  from flask_wtf import FlaskForm
  import asyncio
  from argon2 import PasswordHasher
  from argon2.exceptions import VerifyMismatchError
  from configparser import ConfigParser, NoSectionError
  from datetime import datetime, timedelta
  from jinja2 import TemplateNotFound
  import json
  import os
  from quart_auth import (
    AuthManager,
    login_required,
    Unauthorized,
    AuthUser,
    login_user,
    logout_user,
    current_user,
  )
  import secrets
  import shutil
  import time
  import uvicorn
  from wtforms import (
    # ~ Form,
    # ~ HiddenField,
    # ~ IntegerField,
    PasswordField,
    # ~ RadioField,
    # ~ SelectField,
    StringField,
    SubmitField,
    # ~ TextAreaField,
    validators,
  )
except Exception as e:
  logging.exception(e)
  sys.exit(repr(e))

config_file: str = os.path.join("config.ini")
user_file: str = os.path.join("user.ini")
uvicorn_socket: str | None = None
uvicorn_host: str | None = None
uvicorn_port: str | None = None
log_level: str | None = None
responsável: str = "Responsável"

try:
  config: ConfigParser = ConfigParser()
  config.read(config_file)
  uvicorn_socket = config["uvicorn"]["socket"]
  uvicorn_host = config["uvicorn"]["host"]
  uvicorn_port = int(config["uvicorn"]["port"])
  log_level = config["uvicorn"]["log_level"]
  responsável = config["uvicorn"]["responsavel"]
except (Exception, NoSectionError) as e:
  logging.exception(e)
  sys.exit("Arquivo de configuração não existe ou tá errado")

logging.basicConfig(level = log_level.upper())
logger: logging.Logger = logging.getLogger(__name__)

class ApresentaçãoForm(FlaskForm):
  """Chave da apresentação"""
  chave: StringField = StringField("Chave da apresentação", [
    validators.DataRequired()], default = "não tenho")
  submit: SubmitField = SubmitField("Entrar")

class LoginForm(FlaskForm):
  """Login dos Guri"""
  username: StringField = StringField("Guri", [
    validators.DataRequired()], default = "iuri")
  password: PasswordField = PasswordField(
    "Senha",
    [
      validators.DataRequired(),
      validators.EqualTo(
        "confirm",
        message = f"""A "senha de novo" é a mesma senha, ou seja, a \
senha propriamente dita, que é a senha "senha". Entendeu, ou eu \
compliquei mais ainda?""",
      ),
    ]
  )
  confirm: PasswordField = PasswordField("Senha de novo", [
    validators.DataRequired()])
  submit: SubmitField = SubmitField("Login")

class RegistroForm(FlaskForm):
  """Formulário pra registrar apresentação"""
  chave: StringField = StringField(
    "Chave da apresentação",
    [validators.DataRequired()],
    default = "tudojuntoeminusculosemacento",
  )
  vmix_name: StringField = StringField(
    "Nome do VMIX",
    [validators.DataRequired()],
    default = "iuri",
  )
  vmix_key: StringField = StringField(
    "Chave do VMIX",
    [validators.DataRequired()],
    default = "123456789",
  )
  internet_clicker_code: StringField = StringField(
    "Código do Internet Clicker",
    [validators.DataRequired()],
    default = "naosei",
  )
  submit = SubmitField("Salvar")

app: Quart = Quart(__name__)
app.secret_key: str = secrets.token_urlsafe(32)
AuthManager(app)

@app.route("/", methods = ['GET', 'POST'])
async def apresentacao() -> str:
  """Site pra passar slides"""
  mensagem: str | None = None
  chave: str | None = None
  internet_clicker_url: str | None = None
  vmix_url: str | None = None
  internet_clicker_code: str | None = None
  vmix_name: str | None = None
  vmix_key: str | None = None
  data: str | None = None
  try:
    form: FlaskForm = ApresentaçãoForm(formdata = await request.form)
    if request.method == "POST":
      try:
        chave = form["chave"].data
        if chave not in [None, '', ' ']:
          config: ConfigParser = ConfigParser()
          config.read(user_file)
          internet_clicker_code = config[chave]["internet_clicker_code"]
          vmix_name = config[chave]["vmix_name"]
          vmix_key = config[chave]["vmix_key"]
          data = datetime.fromtimestamp(float(config[chave]["date"]))
          internet_clicker_url = f"""https://www.internetclicker.com?co\
de={internet_clicker_code}&branding=false"""
          vmix_url = f"""https://advanced.vmixcall.com/call.htm?Key=\
{vmix_key}&Name={vmix_name}"""
      except (NoSectionError, KeyError) as e:
        logger.exception(e)
        mensagem = f"""Chave "{chave}" não encontrada. Verifique a \
digitação ou fale com o {responsável}."""
        chave = None
      except Exception as e:
        logger.exception(e)
        mensagem = f"""Em decorrência de problemas técnicos, o site \
não conseguiu processar a informação. Tente novamente ou fale com o \
{responsável}."""
        chave = None
    return await render_template(
      "index.html",
      form = form,
      chave = chave,
      code = internet_clicker_code,
      ic_url = internet_clicker_url,
      vm_url = vmix_url,
      vmix_name = vmix_name,
      vmix_key = vmix_key,
      data = data,
      mensagem = mensagem,
      title = "Passador de slides do Futuro",
    )
  except TemplateNotFound as e:
    logger.exception(e)
    await abort(404)
  except Exception as e:
    logger.exception(e)
    return jsonify(repr(e))

@app.route("/dosguri", methods = ['GET', 'POST'])
# ~ @login_required
async def admin() -> str:
  """Dashboard dos Guri"""
  mensagem: str | None = None
  chave: str | None = None
  internet_clicker_url: str | None = None
  vmix_url: str | None = None
  internet_clicker_code: str | None = None
  vmix_name: str | None = None
  vmix_key: str | None = None
  data: str | None = None
  try:
    form: FlaskForm = ApresentaçãoForm(formdata = await request.form)
    if request.method == "POST":
      try:
        chave = form["chave"].data
        if chave not in [None, '', ' ']:
          config: ConfigParser = ConfigParser()
          config.read(user_file)
          internet_clicker_code = config[chave]["internet_clicker_code"]
          vmix_name = config[chave]["vmix_name"]
          vmix_key = config[chave]["vmix_key"]
          data = datetime.fromtimestamp(float(config[chave]["date"]))
          internet_clicker_url = f"""https://www.internetclicker.com?co\
de={internet_clicker_code}&branding=false"""
          vmix_url = f"""https://advanced.vmixcall.com/call.htm?Key=\
{vmix_key}&Name={vmix_name}"""
      except (NoSectionError, KeyError) as e:
        logger.exception(e)
        mensagem = f"""Chave "{chave}" não encontrada. Verifique a \
digitação ou fale com o {responsável}."""
        chave = None
      except Exception as e:
        logger.exception(e)
        mensagem = f"""Em decorrência de problemas técnicos, o site \
não conseguiu processar a informação. Tente novamente ou fale com o \
{responsável}."""
        chave = None
    return await render_template(
      "admin.html",
      form = form,
      chave = chave,
      code = internet_clicker_code,
      ic_url = internet_clicker_url,
      vm_url = vmix_url,
      vmix_name = vmix_name,
      vmix_key = vmix_key,
      data = data,
      mensagem = mensagem,
      title = "Dashboard dos Guri",
    )
  except TemplateNotFound as e:
    logger.exception(e)
    await abort(404)
  except Exception as e:
    logger.exception(e)
    return jsonify(repr(e))

@app.route("/dosguri/cadastrar", methods = ['GET', 'POST'])
# ~ @login_required
async def server() -> str:
  """Manage Eco server"""
  global servers
  status: bool = False
  message: str | None = None
  exception: Exception | None = None
  try:
    config: ConfigParser = ConfigParser()
    config.read(servers_file)
    function_map: dict = {
      "0": ("Eco Server Status", server_status),
      "1": ("Start Eco Server", server_start),
      "2": ("Stop Eco Server", server_proper_stop),
      "3": ("Restart Eco Server", server_restart),
      "4": ("Advanced - Force Eco Server Stop", server_stop),
    }
    class ServerForm(FlaskForm):
      """Form for server and action selection"""
      server_field: RadioField = RadioField(
        "Select Eco Server",
        [validators.DataRequired()],
        choices = [("0", "None")],
      )
      action_field: RadioField = RadioField(
        "Select Action",
        [validators.DataRequired()],
        choices = [("0", "None")],
      )
      submit: SubmitField = SubmitField("Send")
      async def validate_server_field(form, field) -> None:
        """Populate server selection list"""
        try:
          field.choices = [(index, server) for index, server in \
            enumerate(config.sections())]
        except Exception as e3:
          logger.exception(e3)
          exception = e3
      async def validate_action_field(form, field) -> None:
        """Populate action selection list"""
        field.choices = [(k, v[0]) for k, v in \
          sorted(function_map.items())]
    form: FlaskForm = ServerForm(formdata = await request.form)
    await form.validate_server_field(form.server_field)
    await form.validate_action_field(form.action_field)
    if request.method == "POST":
      try:
        _name: str = config.sections()[int(
          form["server_field"].data)]
        process: Popen = servers[_name]
        _return: dict = await function_map[
          form["action_field"].data][1](process, _name)
        servers[_name] = _return["process"]
        message = _return["message"]
        exception = _return["exception"]
        status = _return["status"]
      except Exception as e2:
        logger.exception(e2)
        exception = e2
    alive: dict[str, bool] = {}
    for _name, process in servers.items():
      alive[_name] = False
      try:
        alive[_name] = (process.poll() is None)
      except (ValueError, AttributeError):
        pass
      except Exception as e1:
        logger.exception(e1)
  except Exception as e:
    logger.exception(e)
    exception = e
  try:
    return await render_template(
      "server.html",
      name = name,
      version = version,
      title = "Eco Server Manager",
      form = form,
      message = message,
      exception = exception,
      alive = alive,
    )
  except Exception as e:
    logger.exception(e)
    return jsonify(repr(e))

async def edit_server(
  name: str,
  path: str,
  password: str,
  boot: bool,
  *args,
  **kwargs,
) -> dict[str, bool | str | Exception | None]:
  """Edit server config on server configuration file"""
  _return: dict[str, bool | str | Exception | None] = {
    "status": False,
    "message": "Could not edit server configuration!",
    "exception": None,
  }
  try:
    config: ConfigParser = ConfigParser()
    if not os.path.exists(os.path.dirname(servers_file)):
      os.makedirs(os.path.dirname(servers_file))
    config.read(servers_file)
    try:
      config.set(name, "boot", str(int(boot)))
      config.set(name, "password", password)
      config.set(name, "path", path)
    except NoSectionError as e2:
      logger.exception(e2)
      config.add_section(name)
      config.set(name, "boot", str(int(boot)))
      config.set(name, "password", password)
      config.set(name, "path", path)
    try:
      shutil.copy(servers_file,
        f"{servers_file}.backup.{datetime.utcnow().timestamp()}")
    except FileNotFoundError:
      pass
    try:
      with open(servers_file, "w+") as srv:
        config.write(srv)
      _return["message"] = f"{name} settings updated."
      _return["status"] = True
    except Exception as e1:
      logger.exception(e1)
      _return["exception"] = e1
  except Exception as e:
    logger.exception(e)
    _return["exception"] = e
  return _return

@app.route("/contador")
@app.route("/contador/")
@app.route("/contador/<chave>")
async def contador(chave: str | None = None) -> dict[str, str | bool]:
  """API do Contador"""
  try:
    if chave not in [None, '', ' ']:
      config: ConfigParser = ConfigParser()
      config.read(user_file)
      return jsonify({"status": True, "date": config[chave]["date"]})
  except Exception as e:
    logger.warning(f"Tentaram recuperar {chave} sem sucesso")
    logger.exception(e)
  return jsonify({"status": False, "date": ""})

@app.route("/set_contador", methods = ['POST'])
async def set_contador(*args, **kwargs) -> dict[str, str | bool]:
  """POST sobrescreve contador"""
  _return: dict[str, bool | str | Exception | None] = {
    "status": False,
    "message": "Não deu certo",
    "exception": None,
  }
  data: dict[str, str] = json.loads(await request.get_data())
  if data["chave"] not in ['', ' ', None]:
    try:
      agora: datetime = datetime.now()
      cronometro: timedelta = timedelta(
        hours = int(data["hora"]),
        minutes = int(data["minuto"]),
        seconds = int(data["segundo"]),
      )
      minutos: datetime = (
        (agora + cronometro) - agora
        ).total_seconds() / 60
      try:
        config: ConfigParser = ConfigParser()
        config.read(user_file)
        config.set(
          data["chave"],
          "date",
          str((agora + cronometro).timestamp()),
        )
        try:
          shutil.copy(user_file,
            f"{user_file}.{datetime.utcnow().timestamp()}.backup.ini")
        except FileNotFoundError as e3:
          _return["exception"] = repr(e3)
        try:
          with open(user_file, "w+") as usr:
            config.write(usr)
          _return["message"] = f"""cronômetro de {data["chave"]} \
atualizado para daqui a {minutos:2.0f} minutos \
({(agora + cronometro).strftime('%H:%M %d/%m')}). Pode levar até dez \
segundos para sincronizar."""
          _return["status"] = True
        except Exception as e2:
          logger.exception(e2)
          _return["exception"] = repr(e2)
      except NoSectionError as e1:
        logger.exception(e1)
        _return["exception"] = repr(e1)
    except Exception as e:
      logger.exception(e)
      _return["exception"] = repr(e)
  return jsonify(_return)

@app.errorhandler(Unauthorized)
@app.route("/entrar", methods = ['GET', 'POST'])
async def login(*e: Exception) -> str:
  """Login dos Guri"""
  logger.exception(e)
  response: str | None = None
  try:
    form: FlaskForm = LoginForm(formdata = await request.form)
    if request.method == "POST":
      try:
        hasher: PasswordHasher = PasswordHasher()
        config: ConfigParser = ConfigParser()
        config.read(login_file)
        user: dict = config[form["username"].data]
        try:
          hasher.verify(
            user.get("password"),
            form["password"].data,
          )
          login_user(AuthUser(user.get("id")))
          if current_user.is_authenticated:
            response = f"""Conectado como {form["username"].data}. \
Sois vós."""
          else:
            response = f"""Acho que a senha tá certa mas o login deu \
errado igual. Reclama pro {responsável}."""
        except VerifyMismatchError as e5:
          logger.exception(e5)
          response = "ERROOOOOOOOOOOOOOOU"
      except KeyError as e4:
        logger.exception(e4)
        response = f"Quem é {form['username'].data}???"
      except Exception as e3:
        logger.exception(e3)
        response = repr(e3)
  except Exception as e2:
    logger.exception(e2)
    response = repr(e2)
  try:
    return await render_template(
      "login.html",
      title = "Login",
      form = form,
      response = response,
    )
  except Exception as e1:
    logger.exception(e1)
    return jsonify(repr(e1))

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
    logger.info(f"""Sistema Operacional sem suporte pra UNIX sockets. \
Usando TCP/IP""")
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
