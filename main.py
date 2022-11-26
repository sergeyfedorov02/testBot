import telebot
from telebot import types

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


    # Запуск бота
    bot.polling(none_stop=True)
