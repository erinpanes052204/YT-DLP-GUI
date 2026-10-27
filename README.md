# YT-DLP GUI

A simple, minimalist Windows app for [yt-dlp](https://github.com/yt-dlp/yt-dlp).
Paste a link, pick the quality, click **Download**. No command line.

> Unofficial. Not affiliated with the yt-dlp or FFmpeg projects.

## Download

Grab **`YT-DLP GUI.exe`** from the [latest release](../../releases/latest) and double-click it.
(Each release also has a `SHA256.txt` so you can verify the file.)

On first launch the app asks to download the tools it needs, once:

| Tool | Size | Why |
|------|------|-----|
| yt-dlp | ~24 MB | the downloader |
| ffmpeg | ~200 MB | joins video + audio, converts to MP3 |
| deno | ~43 MB | needed by yt-dlp for YouTube |

They come directly from the official GitHub releases, are checked against the publishers'
checksums, and are saved in `%LOCALAPPDATA%\YT-DLP GUI\tools`. The `.exe` itself can live
anywhere. (About 450 MB of disk space is used after extraction.)

The app tells you when a new yt-dlp or ffmpeg is available and lets you update, skip, or
ignore it. It also tells you when a new version of the app itself is out.

Already have `yt-dlp.exe` / `ffmpeg.exe`? Put them next to the app and it will use them.

## Features

- Video (up to 4K, MP4 / MKV / WEBM) or audio only (MP3, M4A, OPUS, FLAC, WAV)
- Several links at once (separate with spaces)
- Playlists, thumbnails, metadata, subtitles
- Browser login (cookies) for age-restricted videos
- Light and dark theme

## To Delete

1. Delete the .exe
2. Press Windows + R or search run in the start menu. Paste this and then ok %LOCALAPPDATA%
3. Find the YT-DLP GUI folder and then delete

## Build it yourself

1. Install [Python 3.10+](https://www.python.org/downloads/) (tick *Add to PATH*).
2. Double-click `build.bat`. The app appears in `dist\`.

Releases are built by GitHub Actions: push a tag like `v1.0.1` and
`.github/workflows/build.yml` builds the exe and attaches it to a release.

Before publishing, set `GITHUB_REPO` near the top of `yt-dlp-gui.pyw` to your
`username/repository` (this turns on the update check and the feedback links).

## Please note

Only download content you have the right to download, and respect the terms of the
websites you use. This tool is for personal use.

The yt-dlp logo belongs to the yt-dlp project. yt-dlp is released under the Unlicense;
FFmpeg and deno have their own licenses. This app only downloads them from their official
sources; it does not redistribute them.

## License

[MIT](LICENSE)
