import requests

import TelegramBotYouTube.main as main

test_url = "https://www.youtube.com/watch?v=kRnZCTZn5bQ"
test_duration = 11123
test_video = main.get_information_from_youtube_video(test_url)


def test_get_id_video():

    assert main.get_information_from_youtube_video(test_url) == ("kRnZCTZn5bQ", 1273695, "20221123", 563, "Испания - Коста-Рика. Обзор матча ЧМ-2022 23.11.2022", "Матч ТВ", 3400000, 12825)


def test_get_views_video():
    # Количество просмотров всегда будет расти, поэтому проверим на то, что значение больше взятого на 30.11.2022
    current_views = 1251539
    assert test_video[1] != current_views


def test_get_date_video():
    video_date = "20221123"
    assert test_video[2] == video_date


def test_get_duration_video():
    video_duration = 563
    assert test_video[3] == video_duration


def test_get_title_video():
    video_title = "Испания - Коста-Рика. Обзор матча ЧМ-2022 23.11.2022"
    assert test_video[4] == video_title


def test_get_uploader_video():
    video_uploader = "Матч ТВ"
    assert test_video[5] == video_uploader


def test_get_num_followers_video():
    video_num_followers = 3360000
    assert test_video[6] != video_num_followers


def test_get_num_videos():
    video_num_videos = 12737
    assert test_video[7] >= video_num_videos


def test_get_info_about_url():
    test_url_1 = "https://www.youtube.com/watch?v=kRnZCTZn5bQ"
    test_url_2 = "https://www.youtube.com/watch?v=kRnZCTZ"
    test_url_3 = "какой-то текст.xxx"

    answer_1 = (True, "Хотите получить дополнительную информацию о видео ?")
    answer_2 = (False, "Извините, но данный ролик не существует 😢")
    answer_3 = (False, "Ваше сообщение не является ссылкой на ролик в YouTube 😢")

    assert main.get_info_about_url(test_url_1) == answer_1
    assert main.get_info_about_url(test_url_2) == answer_2
    assert main.get_info_about_url(test_url_3) == answer_3


def test_get_hours_from_video_duration_info():
    cur_hours = 3
    assert main.video_duration_info(test_duration)[0] == cur_hours


def test_get_minutes_from_video_duration_info():
    cur_minutes = 5
    assert main.video_duration_info(test_duration)[1] == cur_minutes


def test_get_seconds_from_video_duration_info():
    cur_seconds = 23
    assert main.video_duration_info(test_duration)[2] == cur_seconds
