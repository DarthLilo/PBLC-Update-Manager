import socket
from threading import Thread
from .Modpacks import Modpacks

class ProtocolHandler:
    
    def handle_connection(client_socket):
        """Handle the connection and process it"""
        
        try:
            data = client_socket.recv(1024).decode("utf-8")
            if not data:
                return
            print(f"Recieved raw URL data {data}")
            modpack_author, modpack_name = Modpacks.SelectedModpackData()
            if Modpacks.Exists(modpack_author,modpack_name) and str(data).__contains__("ror2mm://v1/install/thunderstore.io/"):
                split_mod_data = data.split("/")
                Modpacks.Mods.Add(author=split_mod_data[5],mod=split_mod_data[6],mod_version=split_mod_data[7])
        
        finally:
            client_socket.close()
    
    
    def internal_start_server(host="localhost", port=50152):
        """Starts the HTTP listening server for protocol requests"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen(5)

        print(f"Server started on {host}:{port}")

        while True:
            client_socket, addr = server.accept()
            print(f"Accepted connection from {addr}")
            ProtocolHandler.handle_connection(client_socket)
    
    def send_url_to_instance(url, port=50152):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("localhost", port))
                if url:
                    s.sendall(url.encode())
                    print(f"Passing {url} to server!")
                return False
        
        except ConnectionRefusedError:
            print("No instance found, starting a new one!")
            thread = Thread(target=ProtocolHandler.internal_start_server,daemon=True)
            thread.start()
            return True