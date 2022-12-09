import requests

import TelegramBotYouTube.main as main

test_url = "https://www.youtube.com/watch?v=kRnZCTZn5bQ"
test_duration = 11123


def test_time_step_info():
    time_step_1 = "0.0"
    video_duration_1 = 10
    answer_1 = (False, "Не было введено 3 значения через точку", None)

    time_step_2 = "y.0.x"
    video_duration_2 = 100
    answer_2 = (False, "Было введено 3 значения, но это не числа", None)

    time_step_3 = "0.1.15"
    video_duration_3 = 75
    answer_3 = (True, "Все хорошо", video_duration_3)

    assert main.time_step_info(time_step_1, video_duration_1) == answer_1
    assert main.time_step_info(time_step_2, video_duration_2) == answer_2
    assert main.time_step_info(time_step_3, video_duration_3) == answer_3


def test_get_info_about_url():
    test_url_1 = "https://www.youtube.com/watch?v=kRnZCTZ"
    test_url_2 = "какой-то текст.xxx"

    answer_1 = (False, "Извините, но данный ролик не существует 😢")
    answer_2 = (False, "Ваше сообщение не является ссылкой на ролик в YouTube 😢")

    assert main.get_info_about_url(test_url_1) == answer_1
    assert main.get_info_about_url(test_url_2) == answer_2


def test_get_hours_from_video_duration_info():
    cur_hours = 3
    assert main.video_duration_info(test_duration)[0] == cur_hours


def test_get_minutes_from_video_duration_info():
    cur_minutes = 5
    assert main.video_duration_info(test_duration)[1] == cur_minutes


def test_get_seconds_from_video_duration_info():
    cur_seconds = 23
    assert main.video_duration_info(test_duration)[2] == cur_seconds
