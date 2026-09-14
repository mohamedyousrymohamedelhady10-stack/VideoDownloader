VIDEO DOWNLOADER - full starter project

What is included:
- Native Android UI
- Chaquopy Python 3.14 runtime
- yt-dlp 2026.8.19
- 720p maximum selection
- 8 concurrent fragments
- MP4 output
- MediaStore save to Download
- FFmpegKit maintained 8.1.7 for video/audio merging
- URLs are passed to yt-dlp, which supports many public sites.

Important:
- The FFmpegKit published Android artifact is arm64-v8a, so this build targets arm64-v8a.
- It will not literally support every old 32-bit Android phone.
- It does not bypass DRM, login restrictions, or access controls.
- Some sites may change their extraction rules or require authentication; those cases may fail.

Build:
This project is intended to be built in a modern Android/Gradle environment or CI,
not on the old Windows 7 32-bit computer itself.
