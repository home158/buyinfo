from flask import Flask
import threading
import os
import time

import pt_bot
import pt_config
import pt_scheduler
app = Flask(__name__)
@app.route("/")

def run_web_app():
    port = int(os.environ.get("PORT", "8443"))
    app.run("127.0.0.1", port)

class ProductAttributeFetcherThread(threading.Thread):
    def run(self) -> None:
        while True:
            try:
                pt_scheduler.fetch_product_attributes()
                
                time.sleep(60) 
            except Exception as e:
                print(f"An error occurred: {e}")
                pass

class TelegramAlertSchedulerThread(threading.Thread):
    def run(self) -> None:
        while True:
            try:
                pt_scheduler.telegram_alert_on_db_update()
                time.sleep(30)
            except Exception as e:
                print(f"An error occurred: {e}")
                pass

if __name__ == "__main__":
    if pt_config.TELEGRAM_BOT_MODE == "polling":

        product_attribute_fetcher_thread  = ProductAttributeFetcherThread()
        telegram_alert_scheduler_thread  = TelegramAlertSchedulerThread()

        product_attribute_fetcher_thread.start()
        telegram_alert_scheduler_thread.start()
        pt_bot.application.run_polling()
    else:
        run_web_app()
