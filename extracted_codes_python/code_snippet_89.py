#!./venv/bin/python
import sys
from typing_extensions import runtime
from colors import light_blue, light_red, red, green
from components import AI, Data, FILE, PATH
import getopt
import os
import pickle
from threading import Thread
import time


ACTIVE = True
DATA = Data.get()

HELP = """Usage: %s [OPTIONS] TEXT
        OPTIONS

            -i	--init				Create the config file for this aplication
            -c						Configure the default promt for the AI, changing the behaviour of the AI
            -t						Configure the API-KEY
                --clean             Delete History
                --toggle_hist       toggle the history
                --s2t				Speech to text ui
        """%sys.argv[0]

def init():
    preferences = {
    "Model":"gemini-1.5-flash",
    "API_KEY":"",
    "AI_ROL": "eres un asistente personal, y explicas de forma breve en 2 o 3 parrafos",
    "NAME":"Gemini",
    "HIST": False
    }
    DATA.write(preferences)
    print('Archivos generados correctamente, use %s -t para fijar su api key de gemini'%sys.argv[0])
    print(FILE)
    sys.exit(0)

def config_rol():
    DATA.read()
    print('El rol actual es')
    print(DATA['AI_ROL'])
    print('Escriba a continuación el nuevo rol')
    rol = input()
    DATA.data['AI_ROL'] = rol
    DATA.save()
    sys.exit(0)

def config_token():
    DATA.read()
    print('A continuación escriba o pegue la nueva token')
    DATA.data['API_KEY'] = input()
    DATA.save()
    sys.exit(0)

def clean():
    file = PATH+'.history'
    os.system(f'rm {file}')
    print('Historial de chats eliminados')
    sys.exit(0)

def toggle_hist():
    DATA.read()
    if DATA['HIST']:
        print('Desactivando historial')
    else:
        print('Activando historial')
    DATA.data['HIST'] = not DATA['HIST']
    DATA.save()
    sys.exit(0)

def message(promp_):
    global ACTIVE
    try:
        DATA.read()
    except:
        ACTIVE = False
        raise RuntimeError('Can\'t opens preferences file')
    promp = []
    file = PATH+'.history'

    if os.path.exists(file) and DATA['HIST']:
        with open(file,'rb') as f:
            promp = pickle.load(f)
    else:
        promp.append(
            {'role':'user',
            'parts': ['your rol:'+DATA['AI_ROL']]})

    promp.append(
            {
                'role':'user',
                'parts':promp_
                }
            )

    ai = AI()
    response = ai.doRequest(promp)

    promp.append({
        'role':'model',
        'parts': [response.text]
        })
    if DATA['HIST']:
        with open(file,'wb') as f:
            pickle.dump(promp,f)
            f.close()

    text = ""
    try:
        text = response.text
    except:
        pass
    finally:
        ACTIVE = False
        time.sleep(.5)
        print(light_blue('TU:'),promp_)
        print(light_red(DATA['NAME']+':'),text)

def bar():
    global ACTIVE
    i = 0
    while ACTIVE:
        i = (i%3)+1
        time.sleep(0.1)
        sys.stdout.write("\rPensando "+("."*(i)).ljust(3,' '))
        sys.stdout.flush()
    sys.stdout.write("\r".ljust(40,' ')+'\n')
    sys.stdout.flush()

if __name__=='__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'icth',['init','s2t','configure','help','clean', 'toggle_hist'])
    except getopt.error as msg:
        print(red(msg))
        print(HELP)
        sys.exit(2)

    for option, value in opts:
        if option in ('-i','--init'):
            init()
        if option == '-c':
            config_rol()
        if option == '-t':
            config_token()
        if option in ('-h','--help'):
            print(HELP)
            sys.exit(0)
        if option == '--clean':
            clean()
        if option == '--toggle_hist':
            toggle_hist()


    if len(args) == 0:
        print(red('No puede mandar una consulta vacia'))
        sys.exit(1)

    promp = ""
    while args:
        promp+=args.pop(0)+" "
    if len(promp) > 1:
        Thread(target = bar).start()
        message([promp])
