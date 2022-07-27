## My Pocket Doctor Application

### Description
    A chatbot application that mostly adresses patients to choose a specific medical field and begin asking questions about there case according to the chosen medical field ,the app gives them the appropriate directions and answers to the case.

### Usage
    Run server.py in your external terminal first to open the server connection then run client.py in another terminal then use the gui application .

    Note : the client connection to server will not work unless the user type his name and choose a medical Field and 
    you should run the code from external terminal not from your code editor for the the database to be correctly loaded as it might have an issue in binding the relative path of the database.
    
    if the client didn't interact with the chatbot for 30 seconds(TIMEOUT) the connection to the server would be closed and the chatbot will exit after displaying a message that the server is disconnected and the client will no longer be able to connect with chatbot.

    to install requirements tpye this ==> pip install requirements.txt

    note: a bug may appear in chat area afer sending a message that the letters may dissapear from the chat but if you selected them with mouse crusor they would appear again!