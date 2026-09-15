import json
import os
import shutil
import yt_dlp


def clean_directory(output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for name in os.listdir(output_dir):
        path = os.path.join(output_dir, name)

        try:
            if os.path.isfile(path) or os.path.islink(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
        except Exception:
            pass


def find_file(output_dir, suffix):
    for name in os.listdir(output_dir):
        path = os.path.join(output_dir, name)

        if os.path.isfile(path) and name.endswith(suffix):
            return path

    return None


def download(url, output_dir):

    clean_directory(output_dir)

    # -------------------------------------------------
    # أولًا: نحاول تحميل فيديو + صوت بشكل منفصل
    # بدون أي عملية دمج داخل yt-dlp
    # -------------------------------------------------

    video_opts = {
        "format": "bv*[height<=720]",
        "outtmpl": os.path.join(
            output_dir,
            "%(title)s.video.%(ext)s"
        ),
        "noplaylist": True,
        "concurrent_fragment_downloads": 8,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": True,
    }

    audio_opts = {
        "format": "ba",
        "outtmpl": os.path.join(
            output_dir,
            "%(title)s.audio.%(ext)s"
        ),
        "noplaylist": True,
        "concurrent_fragment_downloads": 8,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": True,
    }

    try:

        # الحصول على معلومات الفيديو فقط
        with yt_dlp.YoutubeDL({
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
        }) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )

        title = str(
            info.get("title")
            or "Video"
        )

        # محاولة تحميل الفيديو فقط
        video_path = None

        try:

            with yt_dlp.YoutubeDL(video_opts) as ydl:

                ydl.download([url])

            for name in os.listdir(output_dir):

                if ".video." in name:

                    path = os.path.join(
                        output_dir,
                        name
                    )

                    if os.path.isfile(path):
                        video_path = path
                        break

        except Exception:
            video_path = None

        # محاولة تحميل الصوت فقط
        audio_path = None

        if video_path:

            try:

                with yt_dlp.YoutubeDL(audio_opts) as ydl:

                    ydl.download([url])

                for name in os.listdir(output_dir):

                    if ".audio." in name:

                        path = os.path.join(
                            output_dir,
                            name
                        )

                        if os.path.isfile(path):
                            audio_path = path
                            break

            except Exception:
                audio_path = None

        # -------------------------------------------------
        # إذا وجدنا فيديو وصوت:
        # أرسلهم إلى Java ليتم الدمج بواسطة FFmpegKit
        # -------------------------------------------------

        if video_path and audio_path:

            return json.dumps({
                "mode": "merge",
                "video": video_path,
                "audio": audio_path,
                "title": title
            })

        # -------------------------------------------------
        # إذا لم يتوفر فيديو منفصل، نحاول تحميل نسخة
        # progressive تحتوي على الفيديو والصوت معًا
        # بدون الحاجة إلى FFmpeg
        # -------------------------------------------------

        clean_directory(output_dir)single_opts = {
            "format": "b[height<=720]",
            "outtmpl": os.path.join(
                output_dir,
                "%(title)s.%(ext)s"
            ),
            "noplaylist": True,
            "concurrent_fragment_downloads": 8,
            "quiet": True,
            "no_warnings": True,
            "restrictfilenames": True,
        }

        with yt_dlp.YoutubeDL(single_opts) as ydl:

            ydl.download([url])

        candidates = []

        for name in os.listdir(output_dir):

            path = os.path.join(
                output_dir,
                name
            )

            if os.path.isfile(path):
                candidates.append(path)

        if len(candidates) == 1:

            return json.dumps({
                "mode": "single",
                "video": candidates[0],
                "title": title
            })

        raise Exception(
            "تعذر العثور على ملف الفيديو الذي تم تحميله."
        )

    except Exception as e:

        raise Exception(
            str(e)
        )
