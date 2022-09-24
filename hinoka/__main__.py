
from hinoka import hinokaBrain, hinokaConfig
from flask import Flask, request
import os
flask_app = Flask(__name__)

@flask_app.route("/COLD_TRIGGER/", methods=["POST"])
def cold_trigger():
    # token match
    if hinokaConfig.COLD_TRIGGER_TOKEN != request.headers.get("token", None):
        return "token mismatch", 401
    
    os.system("kill 1")
    
from threading import Thread
def flask_thread():
    flask_app.run(host="0.0.0.0", port=3000)

flask_thread_obj = Thread(target=flask_thread)
flask_thread_obj.start()

bot = hinokaBrain.create()
bot.run(hinokaConfig.DISCORD_TOKEN)
