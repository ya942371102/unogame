import queue

from loginDialog import LoginDialog
from clientGui import ClientGUI
from event import Event


class Client:
    """
    Client class
    """
    def __init__(self):
        """
        Initialization function
        """
        self.gui = None # Main window
        self.player = None # myself
        self.client_socket = None # The socket that the client connects to the server
        self.events = queue.Queue()  # type:queue.Queue[Event] # Client child thread event queue

    def login(self):
        """
        Client login process.During the client login process, a login dialog is first constructed and the client object is passed in as a parameter.
        After a successful login in the login dialog box, the player in the client object is changed to an appropriate Player object
        :return: True of False
        """
        login_dialog = LoginDialog(self)
        login_dialog.show()
        if self.player is None:
            return False
        return True

    def play(self):
        """
        Build the main window and pass this client object in as arguments
        :return:
        """
        self.gui = ClientGUI(self)
        self.gui.show()


if __name__ == '__main__':
    # Build a client object, and if the login is successful, go to the main window
    client = Client()
    if client.login():
        client.play()
