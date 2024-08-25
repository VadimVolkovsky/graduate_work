import os
import pathlib

import ffmpeg_streaming
from ffmpeg_streaming import Formats


class VideoConverterService:
    def __init__(self):
        self.working_dir: str = f'{pathlib.Path(__file__).parent.parent.absolute()}/media'

    def convert_to_hls(self, filename: str) -> tuple[str, list[str]]:
        """
        Ковертирует видеофайл в HLS (m3u8)
        для корректной работы необходима библиотека ffmpeg
        https://ffmpeg.org/download.html
        Установка на линукс:
        sudo apt install ffmpeg
        """
        path_to_film = f'{self.working_dir}/{filename}'
        video = ffmpeg_streaming.input(path_to_film)
        hls = video.hls(Formats.h264(), hls_time=5)
        hls.auto_generate_representations()

        print(f'Конвертируем видео {filename} в формат m3u8...')
        filename_without_format = filename.split('.')[0]
        file_dir = f'{self.working_dir}/{filename_without_format}_hls'
        hls.output(f'{file_dir}/{filename_without_format}.m3u8')
        print(f'Конвертация {filename} завершена, файлы сохранены в директорию {file_dir}')
        filenames = os.listdir(file_dir)
        return file_dir, filenames

