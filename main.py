from flask import Flask, request, jsonify
import subprocess
import tempfile
import os
import json

app = Flask(__name__)

@app.route('/')
def index():
    return '📥 yt-dlp Video Downloader API aktif!', 200

@app.route('/api/info', methods=['POST'])
def get_info():
    try:
        data = request.get_json()
        url = data.get('url')

        if not url:
            return jsonify({'error': 'URL is required'}), 400

        cmd = ['yt-dlp', '-j', url]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return jsonify({
                'error': 'yt-dlp info failed',
                'details': result.stderr
            }), 500

        video_info = json.loads(result.stdout.strip())

        return jsonify({
            'title': video_info.get('title'),
            'ext': video_info.get('ext'),
            'url': video_info.get('url')  # direct media URL
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download', methods=['POST'])
def download():
    try:
        data = request.get_json()
        url = data.get('url')

        if not url:
            return jsonify({'error': 'URL is required'}), 400

        with tempfile.TemporaryDirectory() as tempdir:
            output_template = os.path.join(tempdir, 'video.%(ext)s')

            cmd = [
                'yt-dlp',
                '-f', 'best',
                '-o', output_template,
                url
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return jsonify({
                    'error': 'Download failed',
                    'details': result.stderr
                }), 500

            # Find downloaded file
            files = os.listdir(tempdir)
            if not files:
                return jsonify({'error': 'No file found'}), 500

            file_path = os.path.join(tempdir, files[0])

            # For now, just return the filename
            return jsonify({
                'message': 'Downloaded successfully',
                'filename': files[0]
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
