# torftp
</br>
<h3>Description: </h3></br>
I was searching for a ftp client that supported tor but couldn't find any, so i coded my own.</br>
A ftp client that supports tor connection written in python3.</br>

<h3>Usage:</h3>
Non tor:
ftptor.py --host ftpserver.com --username ftp --password ftp</br>
Tor:
ftptor.py --host *.onion --tor --username ftp --password ftp</br>
</br>
Currently supports only passive ftp mode.</br></br>
So in order for this to work talking in terms of server side, further configurations need to be done,</br>
like setting a fixed data connection and opening 2 ports on the torrc file for the server.</br>
If anyone can figure out a better way like dynamically locating a new port for every data connection please let me know.
