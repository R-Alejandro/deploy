import socket, json, time, getopt
import threading
HEADER = 64
PORT = 50007
SERVER = socket.gethostbyname(socket.gethostname())
ADDRESS = (SERVER, PORT)
FORMAT = "utf-8"

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def conectar():
    try:
        conexion = cliente.connect(ADDRESS)
    except ConnectionRefusedError:
        print(f"El servidor ha rechazado la conexion")
        return False
    return True

def enviar_msg(msg):
    mensaje = msg.encode(FORMAT)
    long_msg = len(mensaje)
    envia_long = str(long_msg).encode(FORMAT)
    envia_long += b' ' * (HEADER - len(envia_long))
    cliente.send(envia_long)
    cliente.send(mensaje)

def set_identidad(nombre):
    #nombre = input("Nombre de Usuario: ")
    with open("../chat/user.json", "w") as file:
        file.write('{"name": "%s"}' % nombre)
        enviar_msg("start --set_id_name")
        enviar_msg(nombre)

def recibe_mensaje():
    deadline = time.time() + 2.0 #3 segundos de espera
    longitud_msg = 0
    while not longitud_msg:
        cliente.settimeout(deadline - time.time())
        try:
            longitud_msg = cliente.recv(HEADER)
        except socket.timeout as err:
            print(f"el servidor ha tardado en responder {err}")
            break
    if longitud_msg:
        longitud_msg = int(longitud_msg)
        msg = cliente.recv(longitud_msg).decode(FORMAT)
        print(msg)

def help():
    print("""Uso: -<comando> <valor> o --<comando> <valor>
    -h:         (ayuda)     informacion del uso de la app
    -q:         (salir)     desconecta de forma segura
    -m:         (mensaje)   <valor> envia un mensaje
    --set-name: (username)  <valor> cambia el nombre de usuario """)

if __name__ == '__main__':
    try:
        inicia = conectar()
        while inicia:
            op = input(">>>>> ").split()
            try:
                opts, args = getopt.getopt(op, 'hqm',['set-name='])
                for o, a in opts:
                    if o == '-h': help()
                    if o == '-q': 
                        enviar_msg("salir")
                        recibe_mensaje()
                        inicia = False
                    if o == '-m':
                        m = input("== ") 
                        enviar_msg(m)
                    if o == '--set-name': 
                        set_identidad(a)
                        recibe_mensaje()
            except getopt.GetoptError as error:
                print(f"[ERROR DE COMANDO] {error}")
            recibe_mensaje()
    except KeyboardInterrupt or ConnectionResetError:
        enviar_msg("salir")
        print("se ha desconectado bruscamente del servidor")