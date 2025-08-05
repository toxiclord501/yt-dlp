from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route("/api/download", methods=["POST"])
def download_video():
    try:
        data = request.get_json()
        video_url = data.get("url")

        if not video_url:
            return jsonify({"error": "No URL provided"}), 400

        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'forcejson': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            video_title = info.get("title", "untitled")
            formats = info.get("formats", [])

            best = None
            for f in formats:
                if f.get("ext") == "mp4" and f.get("url"):
                    best = f
            if not best:
                return jsonify({"error": "No suitable video format found"}), 404

            return jsonify({
                "title": video_title,
                "download_url": best["url"]
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
