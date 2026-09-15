import json
import os
import shutil
import yt_dlp


def download(url, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # تنظيف أي ملفات متبقية من محاولة سابقة
    for name in os.listdir(output_dir):
        path = os.path.join(output_dir, name)
        try:
            if os.path.isfile(path) or os.path.islink(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
        except Exception:
            pass

    opts = {
        "format": "bv*[height<=720]+ba/b[height<=720]/b",
        "outtmpl": os.path.join(
            output_dir,
            "%(title)s.%(ext)s"
        ),
        "merge_output_format": "mp4",
        "noplaylist": True,
        "concurrent_fragment_downloads": 8,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": True,
    }

    with yt_dlp.YoutubeDL(opts) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        requested = (
            info.get("requested_downloads")
            or []
        )

        # ملف واحد مكتمل بالفعل
        if not requested:

            path = ydl.prepare_filename(info)

            if os.path.isfile(path):

                return json.dumps({
                    "mode": "single",
                    "video": path,
                    "title": str(
                        info.get("title")
                        or "Video"
                    )
                })

        candidates = [
            os.path.join(output_dir, n)
            for n in os.listdir(output_dir)
            if os.path.isfile(
                os.path.join(output_dir, n)
            )
        ]

        video = None
        audio = None

        for item in candidates:

            low = item.lower()

            if (
                low.endswith(
                    (
                        ".mp4",
                        ".webm",
                        ".mkv",
                        ".mov"
                    )
                )
                and video is None
            ):
                video = item

            elif (
                low.endswith(
                    (
                        ".m4a",
                        ".webm",
                        ".opus",
                        ".aac",
                        ".mp3"
                    )
                )
                and audio is None
            ):
                audio = item

        if video and audio:

            title = str(
                info.get("title")
                or "Video"
            )

            return json.dumps({
                "mode": "merge",
                "video": video,
                "audio": audio,
                "title": title
            })

        if len(candidates) == 1:

            return json.dumps({
                "mode": "single",
                "video": candidates[0],
                "title": str(
                    info.get("title")
                    or "Video"
                )
            })

        raise Exception(
            "تعذر العثور على ملفات الفيديو التي تم تحميلها."
        )
