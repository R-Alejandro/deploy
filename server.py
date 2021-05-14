import socket
import threading
import json
from os import environ
#URL = environ['url']
HEADER = 64
PORT = 50007
SERVER = socket.gethostbyname('server-union.herokuapp.com')
#la url va en gethostbyname(URL)
POOL_CLIENTES = [] #
ADDRESS = (SERVER, PORT)
FORMAT = "utf-8"

socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#socket_servidor.bind(ADDRESS)

def existe_username(username):
    with open("./chat/users_table.json") as file:
        data = json.load(file)
        for i in data['users']:
            if username == i['name']:
                return True
    return False

def busca_addr(address):
    with open("./chat/users_table.json") as file:
        data = json.load(file)
        for i in data['users']:
            if address[0] == i['addr']:
                return i
    return False 

def enviar_msg(cliente, msg):
    mensaje = msg.encode(FORMAT)
    long_msg = len(mensaje)
    envia_long = str(long_msg).encode(FORMAT)
    envia_long += b' ' * (HEADER - len(envia_long))
    cliente.send(envia_long)
    cliente.send(mensaje)

def agrega_user(address):
    with open("./chat/users_table.json") as file:
        data = json.load(file)
        temp = data['users']
        user = {"name":"anonimo", "addr": address[0]}
        temp.append(user)
    with open("./chat/users_table.json", "w") as file:
        json.dump(data, file, indent=4)
    print("usuario agregado")
    return "anonimo"

def cambia_username(cliente, address):
    longitud_msg = cliente.recv(HEADER)
    longitud_msg = int(longitud_msg)
    username = cliente.recv(longitud_msg).decode(FORMAT)
    if existe_username(username):
        enviar_msg(cliente, f"[SERVER]: Nombre de usuario {username} ya esta en uso")
        print("Ya existe este nombre")
    else:
        with open("./chat/users_table.json") as file:
            data = json.load(file)
            temp = data['users']
            for i in data['users']:
                if address[0] == i["addr"]:
                    i["name"] = username
        with open("./chat/users_table.json", "w") as file:
            json.dump(data, file, indent=4)
        
        print("nombre cambiado")
        enviar_msg(cliente, f"[SERVER]: Nombre de usuario cambiado a {username}")

def manejo_cliente(cliente, address):

    nombre = busca_addr(address)["name"] if busca_addr(address) else agrega_user(address)
        
    print(f"[NUEVA CONEXION] {nombre} conectado")
    conectado = True
    while conectado:
        try:
            longitud_msg = cliente.recv(HEADER)
        except ConnectionResetError:
            break
        if longitud_msg:
            longitud_msg = int(longitud_msg)
            msg = cliente.recv(longitud_msg).decode(FORMAT)
            print(f"[{nombre} {address[0]}]: {msg}")
            for c in POOL_CLIENTES:
                enviar_msg(c, f"[{nombre}]: "+msg)
            if msg == 'salir':
                enviar_msg(cliente, "[SERVER] Hasta la proxima!!!")
                conectado = not conectado
            if msg == "start --set_id_name":
                cambia_username(cliente, address)
                nombre = busca_addr(address)["name"]

    POOL_CLIENTES.remove(cliente)
    cliente.close()
    print(f"[DESCONEXION] {nombre} desconectado")

def start(socket_server):
    socket_server.listen()
    while True:
        (client_socket, address_client) = socket_server.accept()
        t1 = threading.Thread(target=manejo_cliente, args=(client_socket,address_client))
        t1.start()
        POOL_CLIENTES.append(client_socket)
        print(f"[CONEXIONES ACTIVAS] {threading.activeCount() - 1}")

print(f"[INICIO] inicia server en direccion {ADDRESS}")
start(socket_servidor)
print("[FIN] apaga server")

