# Ez-Tunnel
Easily expose your local nodejs servers to the web with no binary install, account or token required.

![Image](https://github.com/user-attachments/assets/e991be5f-3f76-4adf-a8c8-98804928c02a)

## Requirements 
This relies on Python 3's standard library. Python 3 and git are all that is needed. 

## Usage 
- Clone this repository: 
```
git clone https://github.com/cons0le7/Ez-Tunnel
```
- Copy `tunnel.py` into the same folder where your node server.js exists.
- Execute with `python3 tunnel.py`
- Set port to match your server. This will check for any interfering process on the selected port, give the option to kill them, launch your node server and provide tunneling options.
- Currently there are 2 services available: `serveo.net` and `localhost.run`
- Link for public access to your server will appear in cyan & magenta making it easy to spot. localhost.run will print a QR code after the link but because this script uses multi-threading, the output is staggered so you won't be able to use it. 
- If you have trouble connecting with one, try the other, downtime is to be expected.
- Use Ctrl+C twice to shutdown server. This will stop local node, disconnect from tunnel and kill any remaining processes left on the used port.

