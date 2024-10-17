#!/usr/bin/env -S uv run -q
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "ConfigArgParse",
#   "replicate",
#   "yt_dlp",
# ]
# ///
import os
import logging
from yt_dlp import YoutubeDL
from tempfile import TemporaryDirectory
from pathlib import Path
from configargparse import ArgumentParser, ArgumentDefaultsRawHelpFormatter
import replicate

dry_run = False
yt_dlp_opts = {
    "final_ext": "mp3",
    "format": "bestaudio/best",
    "fragment_retries": 10,
    "ignoreerrors": "only_download",
    "no_warnings": True,
    "noprogress": True,
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "nopostoverwrites": False,
            "preferredcodec": "mp3",
            "preferredquality": "5",
        },
    ],
    "quiet": True,
    "retries": 10,
}


def call_replicate(model, input):
    logging.info(f"Calling Replicate API, {model=}")
    logging.debug(f"Model input: {input}")
    ret = None
    if dry_run:
        logging.info("Skipping call to Replicate API due to --dry-run")
    else:
        ret = replicate.run(model, input=input)
    logging.info("Replicate API call done")
    logging.debug(f"Replicate returned: {ret}")
    return ret


def transcribe(mp3_file):
    res = call_replicate(
        "vaibhavs10/incredibly-fast-whisper:3ab86df6c8f54c11309d4d1f930ac292bad43ace52d10c80d87eb258b3c9f79c",
        input={
            "audio": open(mp3_file, "rb"),
        },
    )
    return res["text"] if res else None


def summarize(text):
    res = call_replicate(
        "meta/meta-llama-3.1-405b-instruct",
        input={
            "system_prompt": "Summarize the text in no more than 150 words.",
            "prompt": text,
        },
    )
    return "".join(res) if res else None


def download(temp_dir, url):
    yt_dlp_opts["outtmpl"] = {"default": str(temp_dir / "res")}
    logging.info(f"Downloading {url} with yt-dlp...")
    logging.debug(f"yt-dlp options: {yt_dlp_opts}")
    ydl = YoutubeDL(yt_dlp_opts)
    ydl.download(url)
    mp3_file = list(temp_dir.glob("*.mp3"))[0]
    logging.info(f"Download done, file {mp3_file}")
    return mp3_file


def main():
    global dry_run
    parser = ArgumentParser(
        default_config_files=["replicate.conf"],
        formatter_class=ArgumentDefaultsRawHelpFormatter,
    )
    parser.add_argument(
        "-t",
        "--replicate-api-token",
        env_var="REPLICATE_API_TOKEN",
        required=True,
        help="Replicate API token - get yours at https://replicate.com/account/api-tokens",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-d", "--debug", env_var="DEBUG", action="store_true")
    parser.add_argument(
        "-n", "--dry-run", action="store_true", help="don't call Replicate API"
    )
    parser.add_argument("url", help="Youtube URL")
    args = parser.parse_args()
    dry_run = args.dry_run
    log_level = logging.ERROR
    if args.verbose:
        log_level = logging.INFO
    if args.debug:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level, format="%(asctime)s %(levelname)s %(message)s")
    os.environ["REPLICATE_API_TOKEN"] = args.replicate_api_token
    logging.debug(f"Arguments: {args}")
    with TemporaryDirectory() as temp_dir:
        text = summarize(transcribe(download(Path(temp_dir), args.url)))
        print(text)


if __name__ == "__main__":
    main()
