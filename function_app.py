import logging, os
import azure.functions as func
from azure.storage.queue import QueueServiceClient

from summarize_news import get_bulletin

app = func.FunctionApp()

@app.schedule(schedule="0 0 22 * * 0-4", arg_name="myTimer", run_on_startup=True,
              use_monitor=False) 
def create_summary(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed.')

    bulletin = send_bulletin_to_queue()

@app.route(route="http_trigger", auth_level=func.AuthLevel.ANONYMOUS)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    bulletin = send_bulletin_to_queue()

    return func.HttpResponse(
        bulletin,
        status_code=200
    )

def send_bulletin_to_queue():
    logging.info('Getting bulletin...')
    bulletin = get_bulletin()

    logging.info('Sending bulletin to queue...')
    connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    queue_name = "bulletin-queue"

    queue_service_client = QueueServiceClient.from_connection_string(connection_string)
    queue_client = queue_service_client.get_queue_client(queue_name)
    queue_client.send_message(bulletin)

    logging.info('Bulletin sent to queue.')
    return bulletin
