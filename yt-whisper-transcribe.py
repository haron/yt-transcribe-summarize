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

# replicate_model = "openai/whisper:cdd97b257f93cb89dede1c7584e3f3dfc969571b357dbcee08e793740bedd854"
# replicate_input = {
#     "model": "large-v3",
#     "translate": False,
#     "temperature": 0,
#     "transcription": "plain text",
#     "suppress_tokens": "-1",
#     "logprob_threshold": -1,
#     "no_speech_threshold": 0.6,
#     "condition_on_previous_text": True,
#     "compression_ratio_threshold": 2.4,
#     "temperature_increment_on_fallback": 0.2,
# }
# replicate_result_key = "transcription"
replicate_model = "vaibhavs10/incredibly-fast-whisper:3ab86df6c8f54c11309d4d1f930ac292bad43ace52d10c80d87eb258b3c9f79c"
replicate_input = {
    "task": "transcribe",
    "language": "None",
    "timestamp": "chunk",
    "batch_size": 64,
    "diarise_audio": False,
}
replicate_result_key = "text"


def transcribe(mp3_file, dry_run=False):
    replicate_input["audio"] = open(mp3_file, "rb")
    logging.info("Running Replicate API client...")
    logging.debug(f"Replicate API input: {replicate_input}")
    if dry_run:
        logging.info("Skipping call to Replicate API due to --dry-run")
    else:
        output = replicate.run(replicate_model, input=replicate_input)
        logging.info("Replicate API call done")
        print(output[replicate_result_key])


def download(args):
    with TemporaryDirectory() as temp_dir:
        path = Path(temp_dir)
        yt_dlp_opts["outtmpl"] = {"default": str(path / "res")}
        logging.info(f"Downloading {args.url} with yt-dlp...")
        logging.debug(f"yt-dlp options: {yt_dlp_opts}")
        ydl = YoutubeDL(yt_dlp_opts)
        ydl.download(args.url)
        logging.info("Download done")
        mp3_file = list(path.glob("*.mp3"))[0]
        transcribe(mp3_file, dry_run=args.dry_run)


def main():
    parser = ArgumentParser(
        default_config_files=["replicate.conf"],
        formatter_class=ArgumentDefaultsRawHelpFormatter,
    )
    parser.add_argument(
        "-t",
        "--token",
        env_var="REPLICATE_API_TOKEN",
        required=True,
        help="Replicate API token - get yours at https://replicate.com/account/api-tokens",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-d", "--debug", env_var="DEBUG", action="store_true")
    parser.add_argument(
        "-n", "--dry-run", action="store_true", help="don't process file with Whisper"
    )
    parser.add_argument("url", help="Youtube URL")
    args = parser.parse_args()
    log_level = logging.ERROR
    if args.verbose:
        log_level = logging.INFO
    if args.debug:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level, format="%(asctime)s %(levelname)s %(message)s")
    os.environ["REPLICATE_API_TOKEN"] = args.token
    logging.debug(f"Arguments: {args}")
    download(args)


if __name__ == "__main__":
    main()
