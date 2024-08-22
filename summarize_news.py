import feedparser, os, requests, json
from datetime import datetime, timedelta

def get_current_articles(feed_url):
    
    # Parse the RSS feed
    feed = feedparser.parse(feed_url)
    
    # Get the current time
    now = datetime.now()    

    # Define the time limit (24 hours ago)
    time_limit = now - timedelta(hours=24)

    # Filter entries
    recent_entries = [entry for entry in feed.entries if datetime(*entry.published_parsed[:6]) > time_limit]

    return recent_entries
        

def create_raw_news_summary(feed):
    # Initialize the summary
    summary = ""

    # Iterate over each entry in the feed
    for entry in feed:
        # Append the title and link of the entry to the summary
        summary += entry.title + "\n"
        summary += entry.summary + "\n"
        summary += entry.link + "\n\n"

    return summary

# a function that sends the news summary to an Azure Open AI model deployment and receives response
def generate_bulletin(raw_news_summary):
    
    # get api key from environment variable
    api_key = os.environ.get("OPENAI_API_KEY")
    endpoint = os.environ.get("OPENAI_ENDPOINT")
    deployment = os.environ.get("OPENAI_DEPLOYMENT")

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    payload = {
        "messages": [
            {
            "role": "system",
            "content": [
                {
                "type": "text",
                "text": "You are a news editor responsible for creating a daily bulletin that is to be read out by a newsreader.  You will be given a series of articles that need to be summarized into the bulletin."
                }
            ]
            },
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": "Here are a series of articles.   Please create a daily news bulletin for reading by our anchor Sally."
                },
                {
                "type": "text",
                "text": raw_news_summary
                }
            ]
            }
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 800
        }

    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version=2024-02-15-preview"

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.RequestException as e:
        raise SystemExit(f"Failed to make the request. Error: {e}")
    
    jsonresponse = response.json()
    # extract the assistant's response from the response
    return jsonresponse["choices"][0]["message"]["content"]

def get_bulletin():
    feed_url = "https://azurefeeds.com/feed/"
    feed = get_current_articles(feed_url)
    raw_news_summary = create_raw_news_summary(feed)
    bulletin = generate_bulletin(raw_news_summary)

    # create a json object containing one property, "bulletin", with the value of the bulletin
    bulletin = json.dumps({"bulletin": bulletin})

    return bulletin

