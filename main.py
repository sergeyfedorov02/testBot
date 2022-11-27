import telebot
from telebot import types

from youtube_dl import YoutubeDL

from pafy import pafy

import cv2

from PIL import Image

import os

import datetime

import config


# Создаем класс нашего видео, чтобы хранить там информацию о нем
class VideoInfo:
    def __init__(self):
        self.url = None  # URL текущего видео
        self.last_GIF = None  # True - есть сформированная гифка, значит можно ее прислать еще раз
        self.id = None  # Id видео
        self.views = None  # Количество просмотров видео
        self.date = None  # Дата выпуска видео
        self.duration = None  # Длительность видео в секундах
        self.title = None  # Название видео
        self.wait_answer = True  # True - ждем ответа из callback функции (обрабатываем нажатие кнопок)
        self.message_inline_button_id = None  # Id сообщения от бота с Inline клавиатурой, чтобы можно было ее удалить
        self.wait_GIF = False  # True - сейчас формируется GIF-ка, чтобы запретить другие действия


# Функция для разбора видео по принятой от пользователя ссылки
def get_information_from_youtube_video(current_youtube_video_link):
    youtube_dl_opts = {
        'ignoreerrors': True,
        'quiet': True,
        # Сюда следует передать файл cookie от аккаунта на YouTube, чтобы бот мог обрабатывать видео 18+
        'cookiefile': 'youtube.com_cookies.txt'
    }

    with YoutubeDL(youtube_dl_opts) as ydl:
        info_dict = ydl.extract_info(current_youtube_video_link, download=False)

        # Такого видео не существует
        if info_dict is None:
            return None
        else:
            cur_video_id = info_dict.get("id", None)
            cur_video_views = info_dict.get("view_count", None)
            cur_video_date = info_dict.get("upload_date", None)
            cur_video_duration = info_dict.get("duration", None)
            cur_video_title = info_dict.get("title", None)
            return cur_video_id, cur_video_views, cur_video_date, cur_video_duration, cur_video_title


# Функция для получения информации о введенном URL
def get_info_about_url(new_youtube_link):
    # Получим информацию о видео
    info_from_video = get_information_from_youtube_video(new_youtube_link)

    # Введенные текст не является ссылкой на ролик на YouTube
    if not new_youtube_link.startswith("https://www.youtube.com/watch?v=") and not new_youtube_link.startswith(
            "youtube.com/watch?v=") and not new_youtube_link.startswith("https://youtu.be/"):
        return False, "Ваше сообщение не является ссылкой на ролик в YouTube 😢"

    # Видео не существует
    elif info_from_video is None:
        return False, "Извините, но данный ролик не существует 😢"

    else:
        return True, "Хотите получить дополнительную информацию о видео ?"


# Функция дляполучения информации и введенных timecodes
def get_info_about_timecodes(timecodes, video_duration):
    split_message = timecodes.split(" ")

    if len(split_message) != 2:
        return False, "Вы не ввели 2 значения! 😢"
    else:
        first_step = time_step_info(split_message[0], video_duration)
        if not first_step[0]:
            return False, "Вы ввели значение <b>под номером один</b> в неправильном формате 😢\n{0}😢".format(
                first_step[1])

        second_step = time_step_info(split_message[1], video_duration)
        if not second_step[0]:
            return False, "Вы ввели значение <b>под номером два</b> в неправильном формате 😢\n{0}😢".format(
                second_step[1])

        return True, "Замечательно, сейчас отправлю вам GIF-ку 😊", [first_step, second_step]


# Дополнительная функция для вычисления длительности видео в часах, минутах и секундах
# Например, для записи 2.20.39 -> hours=2 minutes =20 seconds = 30
def video_duration_info(cur_duration):
    hours = int(cur_duration / 3600)
    minutes = int((cur_duration - hours * 3600) / 60)
    seconds = int((cur_duration - hours * 3600) - minutes * 60)

    return hours, minutes, seconds


# Функция для проверки валидности ввода Таймстепов согласно заданному шаблону:
# Пример: часы.минуты.секунды
def time_step_info(time_step, video_duration):
    split_time_step = time_step.split(".")
    err_message = "Все хорошо"
    info_video_duration = video_duration_info(video_duration)

    # Не ввели три значения через точку
    if len(split_time_step) != 3:
        err_message = "Не было введено 3 значения через точку"
        return False, err_message, None

    # Ввели три значения, но это не числа
    elif not split_time_step[0].isdigit() or not split_time_step[1].isdigit() or not split_time_step[2].isdigit():
        err_message = "Было введено 3 значения, но это не числа"
        return False, err_message, None

    # Ввели три числа, и число часов недопустимое для данного видео
    elif int(split_time_step[0]) > info_video_duration[0]:
        err_message = "Было введено неверное количество часов"
        return False, err_message, None

    # Было введено максимально возможное кол-во часов -> минут должно быть не больше максимального
    elif int(split_time_step[0]) == info_video_duration[0] and int(split_time_step[1]) > info_video_duration[1]:
        err_message = "Неверное количество минут, значение превышает длительность видео"
        return False, err_message, None

    # Было введено НЕ максимально возможное кол-во часов -> минут может быть от 0 до 59
    elif int(split_time_step[0]) != info_video_duration[0] and int(split_time_step[1]) not in range(0, 60):
        err_message = "Неверное количество минут, значение не в диапазоне 0 - 59"
        return False, err_message, None

    # Было введено max часов и max минут -> секунд должно быть не больше максимального
    elif int(split_time_step[0]) == info_video_duration[0] and int(split_time_step[1]) == info_video_duration[1] \
            and int(split_time_step[2]) > info_video_duration[2]:
        err_message = "Неверное количество секунд, значение превышает длительность видео"
        return False, err_message, None

    # Было введено НЕ max часов -> секунд может быть от 0 до 59
    elif int(split_time_step[2]) not in range(0, 60):
        err_message = "Неверное количество секунд, значение не в диапазоне 0 - 59"
        return False, err_message, None

    value = int(split_time_step[0]) * 3600 + int(split_time_step[1]) * 60 + int(split_time_step[2])
    return True, err_message, value


# Функция для получения определенного кадра из заданного видео
# гайд https://clck.ru/32fxCx
def get_current_frames(url, numbers, current_chat_id):
    ydl_opts = {
        'ignoreerrors': True,
        'quiet': True,
        # Сюда следует передать файл cookie от аккаунта на YouTube, чтобы бот мог обрабатывать видео 18+
        'cookiefile': 'youtube.com_cookies.txt'
    }

    video = pafy.new(url, ydl_opts=ydl_opts)

    best = video.getbest(preftype="mp4")

    # Открытие файла с видео
    cap = cv2.VideoCapture(best.url)

    fps = cap.get(cv2.CAP_PROP_FPS)  # Получение fps
    cur_num = 1
    for number in numbers:
        # указываем номер кадра в секундах * fps
        frame_number = number * fps

        # Устанавливаем кадр
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        # Чтение установленного кадра
        ret, frame = cap.read()

        # Ожидание
        # cv2.waitKey()

        # Создадим картинку из нашего кадра
        filename = fr"{current_chat_id}-{cur_num}.png"
        cv2.imwrite(filename, frame)
        cur_num += 1

    # Закроем capture
    # cap.release()
    # cv2.destroyAllWindows()
    return cur_num


# Создадим GIF-ку, состоящую из двух кадров видео
def create_gif_from_images(steps, name, youtube_video_link, cur_chat_id):
    all_numbers = get_current_frames(youtube_video_link, steps, cur_chat_id)

    frames = []
    for frame_number in range(1, all_numbers):
        frame = Image.open(f'{cur_chat_id}-{frame_number}.png')
        frames.append(frame)

    frames[0].save(
        rf'{cur_chat_id}-{name}.gif',
        save_all=True,
        append_images=frames[1:],
        optimize=True,
        duration=250,
        loop=0
    )

    # Удалим созданные фото
    for num in range(1, all_numbers):
        os.remove(fr"{cur_chat_id}-{num}.png")


if __name__ == '__main__':
    # Создание бота при помощи класса TeleBot, куда передадим TOKEN нашего бота
    bot = telebot.TeleBot(config.TOKEN)

    # Для многопользовательского использования введем словарь, где key - chat.id и value - объект класса VideoInfo
    chat_dict = {}


    # Напишем логику работы нашего бота

    # Обработка после запуска бота командой /start
    @bot.message_handler(commands=['start'])
    def welcome(message):
        chat_id = message.chat.id  # Получем id чата

        # Формируется ли сейчас GIF-ка?
        if chat_id in chat_dict.keys() and chat_dict[chat_id].wait_GIF:
            bot.reply_to(message, "🕐 Сейчас формируется GIF-ка, подождите, а затем повторите свой запрос 🕐")

        else:

            # Был перезапуск чата -> удалим Inline клавиатуру, если она осталась
            if chat_id in chat_dict.keys() and chat_dict[chat_id].message_inline_button_id is not None:
                bot.edit_message_reply_markup(chat_id=chat_id, message_id=chat_dict[chat_id].message_inline_button_id,
                                              reply_markup=None)

            # Создаем объект класса VideoInfo, где будет храниться инфо о видео
            video_info = VideoInfo()

            # Создаем в словаре chat_dict пару, где key - id чата, value - информация о видео
            chat_dict[chat_id] = video_info

            # Отсылаем стикер
            sticker = open('AnimatedSticker.tgs', 'rb')
            bot.send_sticker(message.chat.id, sticker)

            # Отсылаем стартовое сообщение
            bot.send_message(chat_id,
                             "Добро пожаловать, {0.first_name}!\n"
                             "Я - <b>{1.first_name}</b>, бот для формирования GIF-ки из видео с YouTube при помощи нескольких таймстепов."
                             "\n\n<b>Доступные команды:</b>"
                             "\n/start - для запуска бота"
                             "\n/help - отображение доступных команд"
                             "\n/getInfoAboutVideo - получение информации о последнем видео (последнее URL)"
                             "\n/getInfoAboutYouTuber - получение информации о последнем Ютубере (последнее URL)"
                             "\n\nПришлите мне ссылку на ролик в YouTube 😊".format(message.from_user, bot.get_me()),
                             parse_mode='html', reply_markup=types.ReplyKeyboardRemove())


    # Обработка сообщения после ввода текста пользователем
    @bot.message_handler(content_types=['text'])
    def message_from_bot(message):
        if message.chat.type == "private":

            chat_id = message.chat.id  # Получим id текущего чата
            current_chat = chat_dict[chat_id]  # Получаем соответствующий нашему chat.id элемент словаря

            current_text = message.text  # получаем введенный пользователем текст (должна быть ссылка на youtube видео)

            # Формируется ли сейчас GIF-ка?
            if current_chat.wait_GIF:
                bot.reply_to(message, "🕐 Сейчас формируется GIF-ка, подождите, а затем повторите свой запрос 🕐")

            else:

                # Была ли уже полученна ссылка на видео от пользователя?
                if current_chat.url is None:

                    # Ссылка не была получена -> обрабатываем полученный текст
                    info_about_url = get_info_about_url(current_text)

                    # Была ли валидная ссылка:
                    if not info_about_url[0]:
                        bot.reply_to(message, info_about_url[1])
                    else:
                        # Получим информацию о видео
                        info_from_video = get_information_from_youtube_video(current_text)

                        # Обновим информацию о полученном видео в словаре chat_dict по key - chat.id
                        current_chat.url = current_text
                        current_chat.id = info_from_video[0]
                        current_chat.views = info_from_video[1]
                        current_chat.date = info_from_video[2]
                        current_chat.duration = info_from_video[3]
                        current_chat.title = info_from_video[4]

                        current_chat.wait_answer = True  # Получили новое видео -> ждем ответа на вопрос

                        # Добавим Inline клавиатуру (после сообщения от бота мы сможем выбрать кнопку для отправки сообщения)
                        markup = types.InlineKeyboardMarkup(row_width=2)
                        item1 = types.InlineKeyboardButton("👍 Да, конечно", callback_data="yep")
                        item2 = types.InlineKeyboardButton("👎 Нет, спасибо", callback_data="nope")
                        markup.add(item1, item2)

                        msg = bot.send_message(chat_id, info_about_url[1],
                                               reply_markup=markup)
                        current_chat.message_inline_button_id = msg.id

                else:  # ссылка уже была получена

                    # Ожидаем ли мы ответ от пользователя на наш вопрос? (была ли нажата кнопка Inline с ответом)
                    if current_chat.wait_answer:

                        # Ждем ответа -> кнопка не была нажата
                        bot.reply_to(message, "Сначала ответьте на вопрос, выбрав кнопку с ответом 👆")
                    else:  # Не ждем ответа -> кнопка уже была нажата

                        # Обработка сообщения после нажатия пользователем кнопки ("🙏 Хочу ввести новую ссылку 🙌")
                        if message.text == "🙏 Хочу ввести новую ссылку 🙌":
                            # Обновим значения url и last_url
                            current_chat.last_GIF = True
                            current_chat.url = None
                            bot.send_message(chat_id, "Хорошо, ожидаю новой ссылки 😀",
                                             reply_markup=types.ReplyKeyboardRemove())

                        # Кнопка не была нажата -> обработаем введенное сообщение
                        else:
                            # Получим информацию о введеных timecodes
                            info_about_timecodes = get_info_about_timecodes(current_text, current_chat.duration)

                            # Были ли введены правильные и валидные значения timecodes ?
                            if not info_about_timecodes[0]:
                                bot.reply_to(message, info_about_timecodes[1], parse_mode='html')
                            else:
                                # timecodes были введены правильно -> формируем GIF
                                current_chat.wait_GIF = True  # Во время формирования GIF нельзя обрабатывать другие запросы
                                bot.send_message(chat_id, info_about_timecodes[1],
                                                 reply_markup=types.ReplyKeyboardRemove())

                                # Получим всем значения введенных таймстепов
                                steps_values = []
                                steps = info_about_timecodes[2]
                                for num in range(len(steps)):
                                    steps_values.append(int(steps[num][2]))

                                # Получаем GIF_ку
                                create_gif_from_images(steps_values, "new", current_chat.url, chat_id)

                                # Отправляем GIF-ку пользователю
                                photo = open(rf"{chat_id}-new.gif", 'rb')
                                bot.send_animation(chat_id, photo)

                                current_chat.wait_GIF = False

                                # Обновим значения url и last_url
                                current_chat.last_url = True
                                current_chat.url = None

                                bot.send_message(chat_id, "Пришлите мне ссылку на ролик в YouTube 😊")


    # Обработка нажатия на кнопки Inline клавиатуру пользователем (реакция бота на ответ пользователя)
    @bot.callback_query_handler(func=lambda call: True)
    def callback_inline(call):
        chat_id = call.message.chat.id  # Получим id текущего чата
        current_chat = chat_dict[chat_id]  # Получаем соответствующий нашему chat.id элемент словаря

        try:
            if call.message:
                if call.data == "yep":
                    year = int(current_chat.date[:4])
                    month = int(current_chat.date[4:6])
                    day = int(current_chat.date[6:])
                    d = datetime.datetime(year, month, day)
                    bot.send_message(chat_id,
                                     "<b>Название видео:</b> {0}\n"
                                     "<b>Дата загрузки видео:</b> {1} {2} {3}\n"
                                     "<b>Количество просмотров:</b> {4}\n"
                                     "<b>Длительность видео в секундах:</b> {5}\n".format(current_chat.title, day,
                                                                                          d.strftime("%B"), year,
                                                                                          current_chat.views,
                                                                                          current_chat.duration),
                                     parse_mode='html')
                elif call.data == "nope":
                    bot.send_message(chat_id, "Хорошо, не будем выводить информацию о видео")

                current_chat.wait_answer = False

                # Удаление Inline кнопки после нажатия (редактирование кнопок)
                bot.edit_message_text(chat_id=chat_id, message_id=current_chat.message_inline_button_id,
                                      text="Хотите получить дополнительную информацию о видео ?", reply_markup=None)
                current_chat.message_inline_button_id = None  # Обновим статус Inline клавиатуры

            # Клавиатура с выбором опции для пользователя (две кнопки)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item = types.KeyboardButton("🙏 Хочу ввести новую ссылку 🙌")
            markup.add(item)

            info_video_duration = video_duration_info(current_chat.duration)

            bot.send_message(chat_id,
                             "Отлично, теперь пришлите мне хотя бы 2 таймстепа в соответствующем формате 😊\n"
                             "<b>Правило ввода:</b> часы.минуты.секунды[Пробел]часы.минуты.секунды[Пробел]и т.д.\n"
                             "<b>Пример ввода краевых значений:</b>{0}.{1}.{2} {3}.{4}.{5}".format(
                                 0, 0, 0, info_video_duration[0], info_video_duration[1], info_video_duration[2]),
                             parse_mode='html', reply_markup=markup)

        except Exception as e:
            print(repr(e))


    # Запуск бота
    bot.polling(none_stop=True)
