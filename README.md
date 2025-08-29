# Ez-Tunnel
Easily expose your local nodejs servers to the web with no account or token required.

## Requirements 
This relies on Python 3's standard library. Python 3 and git are all that is needed. 

## Usage 
- Clone this repository: 
```
git clone https://github.com/cons0le7/Ez-Tunnel
```
- Copy `tunnel.py` into the same folder where your node server.js exists.
- Execute with `python3 tunnel.py`
- Set port to match your server.
- This will check for any interfering process on the selected port, give the option to kill them, launch your node server and provide tunneling options.
- Currently there are 2 services available: `serveo.net` and `localhost.run`
- If you have trouble connecting with one, try the other, downtime is to be expected.
- Use Ctrl+C twice to shutdown server. This will stop local node, disconnect from tunnel and kill any remaining processes left on the used port. 
