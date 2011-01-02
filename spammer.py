#!/usr/bin/python2
# -*- coding: utf-8 -*-

# Copyright 2010,2011 Ivan Sichmann Freitas
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
from getopt import gnu_getopt as getopt
from smtplib import SMTP
import email
import ConfigParser

# Classes
class Email(SMTP):
    # Parte dessa classe foi feita com base no script de spammer feito por
    # Alexandre Tolstenko e Erick Souza
    def __init__(self, receiver, sender, subject, message, attachment_list,
                 login, user, host, port, password):
        message_file = open(message, "r")
        self.msg = email.MIMEMultipart()
        self.msg['Subject'] = subject
        self.msg['From'] = sender
        self.msg.attach(email.MIMEText(message_file.read()))
        message_file.close()
        self.login = login
        self.user = user
        self.host = host
        self.port = port
        self.password = password
        self.attachments = attachment_list

    def spam(self):
        SMTP.__init__(self, self.host, self.port)
        self.ehlo()
        self.starttls()
        self.ehlo()
        self.login(self.user, self.password)
        self.sendmail(self.user, self.receiver, self.msg.as_string())
        self.quit()

# Funções 

# Retorna uma lista com o email institucional do IC de todos os alunos
# matriculados
def lista_de_alunos():
    tmp_file = os.tmpnam()
    os.system("getent passwd | egrep '(/home/cc|/home/ec)' | cut -d ':' -f 1\
              | uniq | sed 's/$/@students.ic.unicamp.br/' > " + tmp_file)
    user_list = []
    for user in open(tmp_file, "r").read():
        user_list.append(user)
    return user_list

# inciando execução do script

# string com a ajuda (deve ser impressa com a opção -h ou --help)
help_string = u"\
Uso: spammer [opções] arquivo_da_mensagem\n\
Opções:\n\
-a, --all    : especifica envio para todos os alunos do IC\n\
-v, --verbose: imprime mais informação durante a execução\n\
-h, --help   : imprime esta ajuda\n\
-q, --quiet  : não imprime nenhuma saída\n\
-y, --ano    : ano a ser enviada a mensagem\n\
-c, --curso  : curso a ser spameado (pode ser cc ou ec)\n\
-t, --titulo : título do spam\n\
-n, --anexo  : caminho para o arquivo anexo da mensagem\
"
shortopts_string = "ahvqy:c:t:n:"
longopts_string = ["all", "help", "verbose", "quiet", "ano=", "curso=", "titulo=", "anexo="]

# FIXME: realizar a leitura de senha durante a execução, evitando armazenamento
# em arquivo
# lendo arquivo de configuração
# Exemplo:
# [defaults]
# host = hostname
# login = login_no_servidor_smtp
# user = usuario_no_servidor_smtp
# port = porta_de_conexao_ao_servidor
# passwd = senha
config = ConfigParser.ConfigParser()
config.read("/etc/caco_spammer.conf", os.path.expandvars("${HOME}/.caco_spammer.conf"))
# lendo parâmetros de linha de comando
opts,file_list = getopt(sys.argv[1:], shortopts_string, longopts_string)
# TODO: buscar um jeito de fazer as opções longas se referirem às curtas (ou vice versa)
opts = dict(opts)
if opts.has_key("-h") or opts.has_key("--help"):
    print help_string
    sys.exit(os.EX_OK) # termina execução com sinal de sucesso

# Avaliando título do email
if opts.has_key("-t"):
    titulo = opts["-t"]
elif opts.has_key("--titulo"):
    titulo = opts["--titulo"]
else:
    print(u"Falta título")
    sys.exit(os.EX_OK)

# Avaliando lista de anexos
if opts.has_key("-n"):
    anexos = opts["-n"]
elif opts.has_key("--anexo"):
    anexos = opts["--anexo"]
else:
    print(u"Falta lista de anexos")

student_list = lista_de_alunos()
# mantendo apenas os endereços especificados pelos parâmetros
# FIXME: fazer com que ocorra um erro caso mais de uma opção conflitante seja passada
if opts.has_key("-y"):
    student_list = filter(lambda x: x.index("ra" + opts["-y"]), student_list)
elif opts.has_key("--ano"):
    student_list = filter(lambda x: x.index("ra" + opts["--ano"]), student_list)

# TODO: implementar a filtragem por curso

# FIXME: parar de usar as variáveis inúteis abaixo
# TODO: implementar a leitura a partir de um arquivo de configuração
CACO = "caco@ic.unicamp.br"
host = config.get("defaults", "host")
login = config.get("defaults", "login")
user = config.get("defaults", "user")
port = config.get("defaults", "port")
passwd = config.get("defaults", "passwd")

email_list = []
for aluno in student_list:
    email_list.append(Email(aluno, CACO, titulo, file_list[0], anexos,
                            login, user, host, port, passwd))

# enviando lista
map(lambda x: x.spam(), email_list)
