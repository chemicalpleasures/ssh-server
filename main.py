import paramiko
import threading

class SSHServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_auth_password(self, username, password):
        # Add authentication logic here (return True if authentication is successful)
        return True

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_exec_request(self, channel, command):
        # Handle the command execution here
        # For simplicity, let's just echo the command back
        channel.send("Command received: {}\n".format(command))
        channel.send_eof()
        return True

# Set up the SSH server
def start_ssh_server():
    host_key = paramiko.RSAKey(filename='./test-rsa.key')  # You can generate a test-rsa.key using ssh-keygen
    port = 2222  # Choose any available port

    server = SSHServer()
    ssh_transport = paramiko.Transport(('localhost', port))
    ssh_transport.add_server_key(host_key)

    print("SSH server listening on port {}".format(port))

    while True:
        try:
            ssh_transport.start_server(server=server)
        except Exception as e:
            print("Error: {}".format(e))
            break

        # Wait for a client connection
        client, addr = ssh_transport.accept()
        print("Connection from {}".format(addr))

        # Start a new thread to handle the connection
        threading.Thread(target=handle_client, args=(client,)).start()

def handle_client(client):
    transport = client.get_transport()
    channel = transport.accept(1)
    if channel is None:
        print("Error: Unable to open channel.")
        return

    channel.send("Welcome to the SSH server!\n")
    channel.send("Type 'exit' to disconnect.\n")

    while True:
        try:
            command = channel.recv(1024).decode('utf-8')
            if not command:
                break

            if command.strip().lower() == 'exit':
                break

            # Execute the command (you can customize this part based on your requirements)
            channel.send("$ {}\n".format(command))
        except Exception as e:
            print("Error: {}".format(e))
            break

    channel.send("Goodbye!\n")
    channel.close()

if __name__ == '__main__':
    start_ssh_server()
