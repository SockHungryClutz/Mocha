"""
Flask server that runs as a seperate process and listens for webhooks from
Ko-fi and pipes the relevant information back to the main Mocha bot
by SockHungryClutz
"""
from flask import Flask, request, abort
from multiprocessing import Queue
import configparser

app = Flask(__name__)

eventQueue = None

koFiLogger = None

config = configparser.ConfigParser()
config.read("MochaConfig.ini")

@app.route("/", methods=["POST"])
def koFiHandler():
    global config, eventQueue, koFiLogger
    data = request.get_json()
    key = request.args.get("key", default="_", type=str)
    # The key argument in the request must match the expected key
    # Weak form of security, but good enough for a discord bot
    if key == config["kofi_config"]["key"]:
        koFiLogger.info("New Ko-Fi message:\n" + str(data))
        eventQueue.put(data)
        return("OK")
    else
        abort(403)

# Initialize, called as a new process
def initListener(returnQueue):
    global app, config, eventQueue, koFiLogger
    eventQueue = returnQueue
    koFiLogger = RollingLogger_Sync(
        config["logging"]["kofi_log_name"],
        config["logging"]["max_log_size"],
        config["logging"]["max_number_logs"],
        config["logging"]["log_verbosity"])
    app.run(port = int(config["kofi_config"]["port"]))
