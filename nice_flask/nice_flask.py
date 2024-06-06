from flask import Flask, render_template, current_app
import requests
import logging

app = Flask(__name__)
app.config['DEBUG'] = True

shown_memes = set()


def get_meme(attempts=5):
    inappropriate_subreddits = ["ImGoingToHellForThis", "OffensiveMemes"]
    url = "https://meme-api.com/gimme"

    for attempt in range(attempts):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            app.logger.info(f"API Response: {data}")

            meme_url = data.get("url", "")
            subreddit = data.get("subreddit", "")

            if subreddit not in inappropriate_subreddits and meme_url not in shown_memes:
                shown_memes.add(meme_url)
                meme_large = data.get("preview", [])[-2] if data.get("preview") else meme_url
                return meme_large, subreddit

            app.logger.info(f"Inappropriate subreddit or repeated meme: {subreddit} - {meme_url}, retrying...")

        except requests.Timeout:
            app.logger.error("Request timed out")
        except requests.RequestException as e:
            app.logger.error(f"Request failed: {e}")
        except (KeyError, IndexError) as e:
            app.logger.error(f"Error processing response: {e}")

    app.logger.warning("Reached maximum attempts for getting a meme")
    return None, None


@app.route("/")
def index():
    app.logger.info(f"Template folder: {current_app.template_folder}")
    meme_pic, subreddit = get_meme()
    if meme_pic and subreddit:
        return render_template("index.html", meme_pic=meme_pic, subreddit=subreddit)
    else:
        return render_template("error.html"), 500


app.config['TEMPLATES_AUTO_RELOAD'] = True

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="0.0.0.0", port=5000)
