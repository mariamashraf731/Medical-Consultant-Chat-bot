import sys
import socket
from threading import Thread,Event
from PyQt5 import QtWidgets,QtCore
import app
import ssl
import time

HOST = socket.gethostbyname(socket.gethostname())
PORT = 9090
TIMEOUT_MESSAGE = "!TIMEOUT" 


class application(app.Ui_MainWindow):
   
    def __init__(self, starterWindow):
        """
        Main loop of the UI
        :param mainWindow: QMainWindow Object
        """
        super(application, self).setupUi(starterWindow)    

        # Setup Button Connections                  
        self.connect_button.clicked.connect(self.check_data)                      #GUI connect button
        self.send_button.clicked.connect(self.message_changed)                    #GUI send msg button
        self.chat_area.setDisabled(True)                                          #GUI chat area
        self.Questions.setDisabled(True)
        self.running = False

    def check_data(self):
        """
        This function connect the application to server if  only
        the user typed his name and chose a specialization  
        """
        # print(self.specialization.currentText())
        if self.client_username.text() and self.specialization.currentIndex() :
            self.connect_server()
        else:
            self.connection_state.setText("You must Enter your name and Choose a specialization !")
            
    def connect_server(self):
        """
        This function responsible for:
        1. Use SSL for socket security handling
        2. Creating a socket object and connect the client to the server
        3. Ensure that the connection is secure using the CA certificate
        4. prepare it for taking a msg from the client through calling self.handle_received_message() with multithreading method
        """
        # Create an SSL context
        context = ssl.SSLContext()
        context.verify_mode = ssl.CERT_REQUIRED

        # Load CA certificate with which the client will validate the server certificate
        context.load_verify_locations("RootCA.pem")

        # Create a new Socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
        # Make the client socket suitable for secure communication
        self.client = context.wrap_socket(self.client_socket)

        # Connect to a given host/port
        self.client.connect((HOST, PORT))

        # Obtain the certificate from the server
        server_cert = self.client.getpeercert()

        # Validate whether the Certificate is indeed issued to the server
        subject = dict(item[0] for item in server_cert['subject'])
        commonName = subject['commonName']
        print(commonName)
        # Check the client certificate bears the expected name as per server's policy
        if not server_cert:
            raise Exception("Unable to retrieve server certificate")

        if commonName != 'Example-Root-CA':
            raise Exception("Incorrect common name in server certificate")

        # Check time validity of the client certificate
        notAfterTimestamp = ssl.cert_time_to_seconds(server_cert['notAfter'])
        notBeforeTimestamp = ssl.cert_time_to_seconds(server_cert['notBefore'])
        currentTimeStamp = time.time()

        if currentTimeStamp > notAfterTimestamp:
            raise Exception("Expired server certificate")

        if currentTimeStamp < notBeforeTimestamp:
            raise Exception("Server certificate not yet active")

        # If Connected Successfully get the username and chosen field to work with
        self.running = True
        self.client_name = self.client_username.text()
        self.spec= self.specialization.currentText()
        self.control_UI()
        self.chatbot(f"Chatbot: Welcome, {self.client_name}","#ff0000")
        self.chatbot("Chatbot: please be aware that if your case is serious you should consult the nearest doctor before taking any tablets at once and any described medicine here is given for general cases!!","#ff0000")

        # Start Handling incoming messages from other client
        # Start a new Timer thread for this Client
        self.client_timer = setInterval(0.3, self.handle_received_message)
            
    def chatbot(self,msg,color):
        #this appends a msg in the chat text area
        message = f"<html><head/><body><p><span style=\" color:{color};\"> {msg} </span></p></body></html>"
        self.chat_area.append(message)
        self.chat_area.setAlignment(QtCore.Qt.AlignLeft)

    def control_UI(self):
        """
        UI  function which disable username and specialization areas and start enabling msgs and chat area according to the chosen specialization
        """
        self.connect_button.setDisabled(True)
        self.client_username.setDisabled(True)
        self.specialization.setDisabled(True)
        self.connection_state.setText("Connection is established successfully!")
        self.chat_area.setDisabled(False)
        self.Questions.setDisabled(False)
        #choosing to send msg from database according to specialization
        if self.spec == "Diabetes":
            self.Questions.setItemText(0, "Choose Your Case Scenario!")
            self.Questions.setItemText(1, "How can I lower my blood glucose level quickly ?")
            self.Questions.setItemText(2, "I've tested for albumin in urine test and it's positive ?")
            self.Questions.setItemText(3, "What are the symptoms of high blood sugar level ?")
            self.Questions.setItemText(4, "Will taking my medicine correct the glucose level ?")
        else:
            self.Questions.setItemText(0, "Choose Your Case Scenario!")
            self.Questions.setItemText(1, "Are there activities I should avoid in the first trimester of pregnancy ?")
            self.Questions.setItemText(2, "Can I drink alcohol while pregnant ?")
            self.Questions.setItemText(3, "Is it true I can get free dental care when I'm pregnant ?")
            self.Questions.setItemText(4, "What foods should I avoid during pregnancy ?")


    def message_changed(self):
        """
        This function begin sending the msg(question) of client to server 
        and print it in the chat area of the sending client
        """
        message = self.Questions.currentText()
        self.send_message(message)
        self.chatbot(f"{self.client_name} : {message}","#0000ff")
        message = f"<html><head/><body><p><span style=\" color:#0000ff;\">{self.client_name} : {message}</span></p></body></html>" 
        # self.chat_area.append(message)
        # self.chat_area.setAlignment(QtCore.Qt.AlignRight)
        self.Questions.setCurrentText("Choose Your Case Scenario!")

    def send_message(self, msg):    
        """
        This function handles sending message to server
        If Send is pressed in the GUI
        """
        # encode msg       
        self.client.send(msg.encode('utf-8'))
        
    def handle_received_message(self):
        """
        This function recieves the reply for client sent msg from the server database
        if this msg is not the TIME_OUT msg it sends it to chat area otherwise
        it closes the connection and the client socket
        """
        while self.running:
            try:
                message = self.client.recv(1024).decode('utf-8')
                print(message)
                # Handle TIMEOUT Connection
                if message == TIMEOUT_MESSAGE:
                    self.client_timer.cancel()
                    self.client.close()
                    self.client_socket.close()
                    self.connection_state.setText("Disconnected From Server!")
                    sys.exit()
                else:
                    # The Actual message if connection authorized
                    self.chatbot(f"Chatbot: {message}","#ff0000")

            # socket was closed for some other reason
            except ConnectionAbortedError:
                break
            except:
                print("Error")
                self.client.close()
                print("[EXITING] Exiting recieving thread .. ")
                sys.exit()
        


# Class to creat an interval for specific function using Threads
class setInterval():
    def __init__(self, interval, action) :
        self.interval = interval
        self.action = action
        self.stopEvent = Event()
        thread = Thread(target=self.__setInterval)
        thread.start()

    def __setInterval(self) :
        nextTime = time.time() + self.interval
        while not self.stopEvent.wait(nextTime-time.time()):
            nextTime += self.interval
            self.action()

    def cancel(self) :
        self.stopEvent.set()



def main():
  
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = application(MainWindow)
    MainWindow.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    
