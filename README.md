# yt-transcribe-summarize

Python script to transcribe and summarize Youtube video (or any video supported by `yt-dlp`), using
models hosted by Replicate.

## Usage

1. [Install UV](https://docs.astral.sh/uv/#getting-started) (or run `pip install -U ConfigArgParse replicate yt_dlp`).

2. Create a [Replicate](https://replicate.com/) account, [enable billing](https://replicate.com/account/billing) (I
**strongly** suggest setting a spend limit to $5 for starters) and get your [API token](https://replicate.com/account/api-tokens).

Then:

    git clone https://github.com/haron/yt-transcribe-summarize.git
    cd yt-transcribe-summarize
    export REPLICATE_API_TOKEN=your-token-here
    ./yt-transcribe-summarize.py https://www.youtube.com/watch?v=dQw4w9WgXcQ

Instead of exporting `REPLICATE_API_TOKEN` every time you want to summarize a video, you can save
it in a config file `replicate.conf`:

    replicate-api-token = ...
