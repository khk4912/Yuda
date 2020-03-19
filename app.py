from flask import *
from flask_compress import Compress
import os
import youtube_dl
from multiprocessing.pool import ThreadPool

compress = Compress()
app = Flask(__name__)
app.secret_key = os.urandom(12)


def downloading(form):
    if form.get("type") == "영상 (mp4)":
        ty = "mp4"
        options = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]",
            "noplaylist": True,
            "outtmpl": "static/downloads/%(title)s.%(ext)s",
            "continuedl": True,
        }
    else:
        ty = "mp3"
        options = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "noplaylist": True,
            "outtmpl": "static/downloads/%(title)s.%(ext)s",
            "continuedl": True,
        }
    with youtube_dl.YoutubeDL(options) as ydl:
        info = ydl.extract_info(form.get("link"), download=True)
    return info, ty


@app.route("/")
def main():
    return render_template("main.html")


@app.route("/download_finish", methods=["POST", "GET"])
def download_page():
    if request.method == "POST":
        try:
            form = request.form
            # ydl.download([form.get("link")] )
            pool = ThreadPool(processes=1)
            async_result = pool.apply_async(downloading, (form,))
            info = async_result.get()
            info, ty = info
            pool.close()
            pool.join()
            title = info["title"]
            title = title.replace("/", "_")
            title = title.replace("?", "")
            return render_template(
                "download_finish.html",
                title=title,
                uploader=info["uploader"],
                ext=ty,
                thumbnail=info["thumbnail"],
            )
        except:
            return redirect(url_for("main"))
    else:
        return redirect(url_for("main"))


@app.route("/subs")
def subs():
    return render_template("subs.html")


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", threaded=True, port=80)
