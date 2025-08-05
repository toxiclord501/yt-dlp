from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

# Platform detection
def detect_platform(url):
    if 'instagram.com' in url:
        return 'instagram'
    elif 'tiktok.com' in url:
        return 'tiktok'
    elif 'youtube.com' in url or 'youtu.be' in url:
        return 'youtube'
    elif 'facebook.com' in url:
        return 'facebook'
    else:
        return 'unknown'

@app.route('/')
def index():
    return '✅ Downloader API aktif!'

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'status': 'error', 'message': 'No URL provided'}), 400

    platform = detect_platform(url)

    try:
        if platform == 'instagram':
            res = requests.post('https://igram.world/api/', data={"url": url})
            match = re.search(r'https://[^\s"]+\.mp4', res.text)
            if match:
                return jsonify({
                    "status": "ok",
                    "platform": "instagram",
                    "download_url": match.group()
                })

        elif platform == 'tiktok':
            headers = {"User-Agent": "Mozilla/5.0"}
            session = requests.Session()
            html = session.get("https://snaptik.app", headers=headers).text
            token = re.search(r'name="token" value="(.*?)"', html)
            if token:
                res = session.post("https://snaptik.app/abc2.php", data={
                    "url": url,
                    "token": token.group(1)
                }, headers=headers)
                match = re.search(r'https://[^\s"]+\.mp4', res.text)
                if match:
                    return jsonify({
                        "status": "ok",
                        "platform": "tiktok",
                        "download_url": match.group()
                    })

        elif platform == 'youtube':
            html = requests.get(f"https://api.vevioz.com/@api/button/mp3/{url}").text
            match = re.search(r'href=\"(https://[^\s]+\.mp3)', html)
            if match:
                return jsonify({
                    "status": "ok",
                    "platform": "youtube",
                    "download_url": match.group(1)
                })

        elif platform == 'facebook':
            res = requests.post("https://fdown.net/download.php", data={"URLz": url})
            match = re.search(r'href="(https://[^\s]+\.mp4)"', res.text)
            if match:
                return jsonify({
                    "status": "ok",
                    "platform": "facebook",
                    "download_url": match.group(1)
                })

        return jsonify({
            "status": "error",
            "message": f"Failed to extract video URL from {platform}"
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
