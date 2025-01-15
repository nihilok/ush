The easiest way to interact with this API is to grab the CLI script from [here](https://gist.githubusercontent.com/nihilok/c50452133efa61fefb1021afd074b435/raw/ush_cli.py)

```bash
wget https://gist.githubusercontent.com/nihilok/c50452133efa61fefb1021afd074b435/raw/ush_cli.py
chmod +x ush_cli.py
# The first time you run the script, the username is required (it will be stored in the config file)
./ush_cli.py https://google.com --username <username>
```

Subsequent runs will not require the username to be passed as an argument. The script will use the username stored in the config file.

```bash
./ush_cli.py https://google.com
```