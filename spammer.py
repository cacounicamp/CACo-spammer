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
from smtplib import SMTP
import email
import ConfigParser
from optparse import OptionParser

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

if __name__ == "__main__":
    MIN_ARGS = 1 # número mínimo de argumentos
    # Exemplo:
    # [defaults]
    # host = hostname
    # login = login_no_servidor_smtp
    # user = usuario_no_servidor_smtp
    # port = porta_de_conexao_ao_servidor
    # passwd = senha
    config = ConfigParser.ConfigParser()
    config.read(["/etc/caco_spammer.conf", os.path.expandvars("${HOME}/.caco_spammer.conf")])

    # lendo parâmetros de linha de comando
    # idéia contribuída por Gustavo Serra Scalet
    options = {
        '-a': ['--all', u'Envia emails para todos os alinus do IC', False],
        '-q': ['--quiet', u'Não imprime nada na saída padrão', False],
        '-v': ['--verbose', u'Imprime informações de status', True],
        '-y': ['--ano', u'Indica qual o ano a receber os emails (dois \
               dígitos', ''],
        '-c': ['--curso', u'Indica qual curso (cc, ec, se não for especificada \
               é para todos)', ''],
        '-t': ['--titulo', u'Titulo da mensage (obrigatorio)', ''],
        '-n': ['--anexo', u'Lista de arquivos anexos', '']
    }
    options_list = "".join(["[%s %s] " % (o, options[o][0]) for o in options])
    options_list += u"arquivo_da_mensagem"
    opts = OptionParser("Spammer %s" %options_list)
    for o in options:
        if type(options[o][2]) is bool:
            opts.add_option(o, options[o][0],
                            action="store_true",
                            help=options[o][1],
                            default=options[o][2])
        elif type(options[o][2]) is str:
            opts.add_option(o, options[o][0],
                            action="store",
                            help=options[o][1],
                            default=options[o][2])
    (opt, args) = opts.parse_args(sys.argv)
    if len(args) < MIN_ARGS + 1:
        print u"""\
ERRO: número insuficiente de argumentos
Use a opção -h para ver o modo de uso do aplicativo"""
        sys.exit(os.EX_USAGE)
    # construindo um dicionário com as opções
    opt_str = format(opt)[1:-1].split(',')
    opt = {}
    for i in opt_str:
        _i = i.strip().split(':')
        rvalue = _i[1].strip()
        if type(eval(rvalue)) is bool:
            opt[_i[0].strip("'").strip()] = eval(rvalue)
        else: # é booleano
            opt[_i[0].strip("'").strip()] = rvalue.strip("'").strip()

    # Avaliando título do email
    if opt.has_key("titulo"):
        titulo = opt["titulo"]
    else:
        print(u"Falta título")
        sys.exit(os.EX_USAGE)

    # Avaliando lista de anexos
    if opt.has_key("anexo"):
        anexos = opt["anexo"]
    else:
        if opt["verbose"]:
            print(u"Falta lista de anexos")

    student_list = lista_de_alunos()
    # mantendo apenas os endereços especificados pelos parâmetros
    if opt.has_key("ano"):
        student_list = filter(lambda x: x.index("ra" + opts["--ano"]), student_list)

    # TODO: implementar a filtragem por curso

    # FIXME: parar de usar as variáveis inúteis abaixo
    # FIXME: verificar pela existência das opções abaixo na configuração
    CACO = "caco@ic.unicamp.br"
    host = config.get("defaults", "host")
    login = config.get("defaults", "login")
    user = config.get("defaults", "user")
    port = config.get("defaults", "port")
    passwd = config.get("defaults", "passwd")
    # debug
    print host, login, user, port, passwd

    email_list = []
    for aluno in student_list:
        email_list.append(Email(aluno, CACO, titulo, file_list[0], anexos,
                                login, user, host, port, passwd))

    # enviando lista
    map(lambda x: x.spam(), email_list)
