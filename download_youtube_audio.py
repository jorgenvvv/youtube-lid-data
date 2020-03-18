#!/usr/bin/env python3

import argparse
import csv
import json
import logging
import os
import random
import sys

import youtube_dl
from tqdm import tqdm

YTDL_OPTS = {
    'format': 'bestaudio/best',
    'writeinfojson': True,
    'noplaylist': True,
    'nooverwrites': True,
    'ignoreerrors': True,
    'quiet': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio'
    }],
    # Ignore livestreams
    'match_filter': youtube_dl.utils.match_filter_func('!is_live')
}

def read_youtube_links(file_path: str) -> list:
    with open(file_path, encoding='utf-8') as fin:
        links = [link.strip() for link in fin]

    random.shuffle(links)

    return links


def download_video(link: str, language: str, output_path: str, max_video_duration: int) -> int:
    YTDL_OPTS['outtmpl'] = os.path.join(
        output_path, language, '%(id)s.%(ext)s')

    current_output_path = os.path.join(output_path, language)

    os.makedirs(current_output_path, exist_ok=True)

    with youtube_dl.YoutubeDL(YTDL_OPTS) as ydl:
        video_url = f'https://www.youtube.com/watch?v={link}'

        video_metadata = ydl.extract_info(video_url, download=False)

        if (video_metadata is not None and video_metadata['duration'] < max_video_duration):
            ydl.download([video_url])

            return video_metadata['duration']


def format_duration(seconds: int) -> str:
    hours = seconds / 60 / 60
    result = f'{round(hours, 2)}h'

    return result


def download_links(links: list, language: str, output_path: str, max_video_duration: int, total_duration_limit: int) -> None:
    total_duration = 0

    with tqdm(total=len(links)) as pbar:
        pbar.set_description('Downloading audio')

        for i, link in enumerate(links):
            downloaded_video_duration = download_video(
                link, language, output_path, max_video_duration)

            if downloaded_video_duration is not None:
                total_duration = total_duration + downloaded_video_duration

            if (total_duration >= total_duration_limit):
                logging.info(
                    f'Downloads for language {language} finished successfully. Downloaded {format_duration(total_duration)} of audio.')
                exit()

            pbar.update(i)
            pbar.set_postfix(
                {
                    'downloaded_duration': format_duration(total_duration),
                    'language': language
                }
            )

    logging.info(
        f'Downloads for language {language} finished. There was not enough videolinks to download {format_duration(total_duration_limit)} of audio. Downloaded {format_duration(total_duration)} of audio.')


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    parser = argparse.ArgumentParser(
        description='Given a file with Youtube video ids download specified amount of hours (or less) of audio from videos.'
    )

    parser.add_argument('-i', '--input', type=str,
                        help='input file, that contains video ids')
    parser.add_argument('-o', '--output-path', type=str, default='./',
                        help='output path, where to store the downloaded audio files')
    parser.add_argument('--max-video-duration', type=int, default=3600,
                        help='maximum duration of single downloadable video (in seconds), longer videos will not be downloaded')
    parser.add_argument('--total-duration', type=int, default=540000,
                        help='total duration how much audio should be attempted to be downloaded (if there is not enough video ids then less audio will be downloaded)')

    args = parser.parse_args()

    if not len(sys.argv) > 1:
        parser.print_help()
        parser.exit()

    if args.input:
        if os.path.isfile(args.input):
            links = read_youtube_links(args.input)

            language_code = os.path.basename(args.input).split('_')[0]

            download_links(links, language_code, args.output_path,
                           args.max_video_duration, args.total_duration)

        elif os.path.isdir(args.input):
            if not os.listdir(args.input):
                print('Provided input directory does not contain any files')
                parser.exit()

            logging.info(
                f'Downloading audio using links from {args.input}')

            for file in os.listdir(args.input):
                current_file = os.path.join(args.input, file)
                if os.path.isfile(current_file):
                    logging.info(f'Dowloading links using file {file}')

                    links = read_youtube_links(current_file)

                    language_code = os.path.basename(current_file).split('_')[0]

                    download_links(links, language_code, args.output_path,
                                   args.max_video_duration, args.total_duration)

        else:
            print('Invalid input file or directory')
            parser.exit()
