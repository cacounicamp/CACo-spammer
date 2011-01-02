#!/usr/bin/python2
# -*- coding: utf-8 -*-

# Copyright 2010 Ivan Sichmann Freitas
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

# Classes
class Email(SMTP):
    # Parte dessa classe foi feita com base no script de spammer feito por
    # Alexandre Tolstenko e Erick Souza
    def __init__(self, receiver, sender, subject, message, attachment_list,
                 login, user):
        message_file = open(message, "r")
        SMTP.__init__(self) # FIXME: colocar os parâmetros adequados aqui
        self.msg = email.MIMEMultipart()
        self.msg['Subject'] = subject
        self.msg['From'] = sender
        self.msg.attach(email.MIMEText(message_file.read()))
        message_file.close()
        self.login = login
        self.user = user
        self.message_path = message

    #def spam(self):


# Funções 
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
help_string =u"\
        Uso: spammer [opções] arquivo_da_mensagem\
        Opções:\
        -a, --all    : especifica envio para todos os alunos do IC\
        -v, --verbose: imprime mais informação durante a execução\
        -h, --help   : imprime esta ajuda\
        -q, --quiet  : não imprime nenhuma saída\
        -y, --ano    : ano a ser enviada a mensagem\
        -c, --curso  : curso a ser spameado (pode ser cc ou ec)\
        -t, --titulo : título do spam\
        -n, --anexo  : caminho para o arquivo anexo da mensagem\
        "
shortopts_string = "ahvqy:c:t:n:"
longopts_string = ["all", "help", "verbose", "quiet", "ano=", "curso=", "titulo=", "anexo="]

opts,file_list = getopt(sys.argv[1:], shortopts_string, longopts_string)
opts = dict(opts)
if opts.has_key("-a") or opts.has_key("--help"):
    print help_string
    sys.exit(os.EX_OK) # termina execução com sinal de sucesso
