import logging
import azure.functions as func
from summarize_news import get_bulletin

app = func.FunctionApp()

@app.schedule(schedule="0 0 22 * * 0-4", arg_name="myTimer", run_on_startup=True,
              use_monitor=False) 
def create_summary(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed.')

@app.route(route="http_trigger", auth_level=func.AuthLevel.ANONYMOUS)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    bulletin = get_bulletin()

    return func.HttpResponse(
        bulletin,
        status_code=200
    )
