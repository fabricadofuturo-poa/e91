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
    # ~ flash,
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
events_file: str = os.path.join("events.ini")
users_file: str = os.path.join("users.ini")
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
  password: PasswordField = PasswordField("Senha",
    [validators.DataRequired()])
  submit: SubmitField = SubmitField("Login")

class RegisterForm(FlaskForm):
  """Registro dos Guri"""
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
  submit: SubmitField = SubmitField("Registrar")

class CadastroForm(FlaskForm):
  """Formulário pra cadastrar apresentação"""
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
          config.read(events_file)
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
@app.route("/dosguri/", methods = ['GET', 'POST'])
@login_required
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
          config.read(events_file)
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
@login_required
async def cadastrar() -> str:
  """Cadastro dos Guri"""
  message: str | None = None
  exception: str | None = None
  try:
    config: ConfigParser = ConfigParser()
    if not os.path.exists(events_file):
      try:
        os.makedirs(os.path.dirname(events_file))
      except FileNotFoundError:
        pass
    config.read(events_file)
    form: FlaskForm = CadastroForm(formdata = await request.form)
    if request.method == "POST":
      try:
        chave: str = form["chave"].data
        if chave not in config.sections():
          config.add_section(chave)
        for item in ("vmix_name", "vmix_key", "internet_clicker_code"):
          try:
            config.set(chave, item, form[item].data)
          except NoSectionError:
            config.add_section(chave)
            config.set(chave, item, form[item].data)
        config.set(chave, "date", "1")
        try:
          shutil.copy(events_file,
            f"{events_file}.{datetime.utcnow().timestamp()}.backup.ini")
        except FileNotFoundError as e:
          logger.exception(e)
        try:
          with open(events_file, "w+") as event:
            config.write(event)
          message = f"Informações para {chave} inseridas."
        except Exception as e:
          logger.exception(e)
          exception = repr(e)
      except Exception as e:
        logger.exception(e)
        exception = repr(e)
    events: dict[str, dict[str, str]] = { \
      section:dict(config.items(section)) \
      for section in \
      config.sections() \
    }
  except Exception as e:
    logger.exception(e)
    exception = repr(e)
  try:
    return await render_template(
      "cadastro.html",
      title = "Cadastro dos Guri",
      form = form,
      message = message,
      exception = exception,
      events = events,
    )
  except Exception as e:
    logger.exception(e)
    return jsonify(repr(e))

@app.route("/contador")
@app.route("/contador/")
@app.route("/contador/<chave>")
async def contador(chave: str | None = None) -> dict[str, str | bool]:
  """API do Contador"""
  try:
    if chave not in [None, '', ' ']:
      config: ConfigParser = ConfigParser()
      config.read(events_file)
      return jsonify({"status": True, "date": config[chave]["date"]})
  except Exception as e:
    logger.warning(f"Tentaram recuperar {chave} sem sucesso")
    logger.exception(e)
  return jsonify({"status": False, "date": ""})

## TODO: Usar JWT, @login_required não tem como
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
        config.read(events_file)
        config.set(
          data["chave"],
          "date",
          str((agora + cronometro).timestamp()),
        )
        try:
          shutil.copy(events_file,
            f"{events_file}.{datetime.utcnow().timestamp()}.backup.ini")
        except FileNotFoundError as e3:
          _return["exception"] = repr(e3)
        try:
          with open(events_file, "w+") as event:
            config.write(event)
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

@app.route("/dosguri/registrar", methods = ['GET', 'POST'])
@login_required
async def register() -> str:
  """Register Form"""
  message: str | None = None
  exception: Exception | None = None
  try:
    config: ConfigParser = ConfigParser()
    config.read(users_file)
    form: FlaskForm = RegisterForm(formdata = await request.form)
    if request.method == "POST":
      try:
        hasher: PasswordHasher = PasswordHasher()
        user: str = form["username"].data
        hashed_password: str = hasher.hash(form["password"].data)
        try:
          hasher.verify(
            form["confirm"].data,
            hashed_password,
          )
        except:
          raise
        if not user in config.sections():
          config.add_section(user)
        config.set(user, "password", hashed_password)
        config.set(user, "id", str(config.sections().index(str(user))))
        try:
          shutil.copy(users_file,
            f"{users_file}.{datetime.utcnow().timestamp()}.backup.ini")
        except FileNotFoundError:
          pass
        try:
          with open(users_file, "w+") as senhas:
            config.write(senhas)
          message = f"{user} registrado. É os guri, pai"
        except Exception as e1:
          logger.exception(e1)
          exception = e1
      except Exception as e2:
        logger.exception(e2)
        exception = e2
    users: dict[str, dict[str, str]] = {
      section:dict(config.items(section)) \
      for section in \
      config.sections() \
    }
    senha_lista: list[str] = [
      'cocacola',
      'blink182',
      'forfun',
      'goodcharlote',
      'mychemicalromance',
      'nxzero',
      'restart',
      'simpleplan',
      'violãosetecorda',
      'cagardeportaaberta',
      'deixarpratosujonamissioncontrol',
      'deixarcanecasujanamissioncontrol',
    ]
  except Exception as e1:
    logger.exception(e1)
    exception = e1
  try:
    return await render_template(
      "register.html",
      title = "Registrar os Guri",
      form = form,
      message = message,
      exception = exception,
      users = users,
      senha_lista = senha_lista,
    )
  except Exception as e:
    logger.exception(e)
    return jsonify(repr(e))

@app.errorhandler(Unauthorized)
@app.route("/dosguri/entrar", methods = ['GET', 'POST'])
async def login(*e: Exception) -> str:
  """Login dos Guri"""
  logger.exception(e)
  message: str | None = None
  exception: str | None = None
  login: bool = False
  try:
    if await current_user.is_authenticated:
      login = True
    form: FlaskForm = LoginForm(formdata = await request.form)
    if request.method == "POST":
      try:
        hasher: PasswordHasher = PasswordHasher()
        config: ConfigParser = ConfigParser()
        config.read(users_file)
        user: dict = config[form["username"].data]
        try:
          hasher.verify(
            user.get("password"),
            form["password"].data,
          )
          login_user(AuthUser(user.get("id")))
          if await current_user.is_authenticated:
            login = True
            message = f"""Não sei como, mas tu acertou a senha. \
Conectado como {form["username"].data}. É os guri."""
          else:
            message = f"""Acho que a senha tá certa mas o login deu \
errado igual. Reclama pro {responsável}."""
        except VerifyMismatchError as e5:
          logger.exception(e5)
          message = "ERROOOOOOOOOOOOOOOU"
          exception = repr(e5)
      except KeyError as e4:
        logger.exception(e4)
        message = f"Quem é {form['username'].data}???"
      except Exception as e3:
        logger.exception(e3)
        exception = repr(e3)
  except Exception as e2:
    logger.exception(e2)
    exception = repr(e2)
  try:
    return await render_template(
      "login.html",
      title = "Login dos Guri",
      form = form,
      message = message,
      exception = exception,
      login = login,
    )
  except Exception as e1:
    logger.exception(e1)
    return jsonify(repr(e1))

@app.route("/dosguri/sair")
async def logout() -> str:
  """Logout route"""
  try:
    while (await current_user.is_authenticated):
      logout_user()
  except Exception as e:
    logger.exception(e)
    return jsonify(repr(e))
  try:
    return await render_template(
      "login.html",
      title = "Sair",
      login = True,
      logout = True,
    )
  except Exception as e:
    logger.exception(e)
    return jsonify(repr(e))

@app.errorhandler(TemplateNotFound)
@app.errorhandler(404)
@app.route("/quedelhe")
async def not_found(*e: Exception) -> str:
  """404"""
  logger.exception(e)
  try:
    return await render_template_string("""<h1>Que-de-lhe&quest;</h1>\
<p>Alguém deve ter te mandado o link errado, provavelmente de \
propósito, mas existe uma possibilidade de tu ter cagado e digitado \
errado.</p><p><a href='{{url_for("login") }}'>voltar</a></p>\
"""), 404
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
    sys.exit("TCHAU")
  except (
    OSError,
    NotImplementedError,
    asyncio.exceptions.CancelledError,
  ):
    logger.info(f"""Sistema Operacional sem suporte pra UNIX sockets. \
Usando TCP/IP""")
  try:
    uvicorn.run(
      app,
      host = uvicorn_host,
      port = uvicorn_port,
      forwarded_allow_ips = "*",
      proxy_headers = True,
      timeout_keep_alive = 0,
      log_level = log_level.lower(),
    )
    sys.exit("TCHAU")
  except Exception as e:
    logger.exception(e)
    logger.critical("Uvicorn não funcionou de jeito nenhum")
  try:
    app.run()
  except Exception as e:
    logger.exception(e)
