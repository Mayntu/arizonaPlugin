from dotenv import load_dotenv
from os import environ
from enum import Enum
try: load_dotenv()
except Exception as e: print(e)
BOT_TOKEN : str = environ.get("BOT_TOKEN")
YOOMONEY_CLIENT_ID : str = environ.get("YOOMONEY_CLIENT_ID")
YOOMONEY_CLIENT_SECRET : str = environ.get("YOOMONEY_CLIENT_SECRET")
YOOMONEY_ACCESS_TOKEN : str = environ.get("YOOMONEY_ACCESS_TOKEN")
YOOMONEY_WALLET_ID : str = environ.get("YOOMONEY_WALLET_ID")
TOKEN_PASS : str = environ.get("TOKEN_PASS")
ADMIN_CHAT_IDS = environ.get("ADMIN_CHAT_IDS").split(",")
SCRIPT_DRIVE_URL : str = environ.get("SCRIPT_DRIVE_URL")

SCRIPT_COST : int = 150


class ScriptStore(Enum):
    ONE_MONTH = (1, 150)
    THREE_MONTH = (3, 350)
    SIX_MONTH = (6, 590)

    def __init__(self, duration_month : int, cost : int) -> None:
        self.duration_month = duration_month
        self.cost = cost
    
    @staticmethod
    def find_by_duration(duration_month : int) -> "ScriptStore":
        for script in ScriptStore:
            if duration_month == script.duration_month:
                return script
        
        return None


class RedisKeys(Enum):
    REPORTS = ("reports", 600)
    IDEAS = ("ideas", 600)
    def __init__(self, key_name : str, key_duration : int) -> None:
        self.key_name = key_name
        self.key_duration = key_duration


class QueryDataKeys(Enum):
    REPORTS = ("repots_page_number_{current_page}", "reports_ignore", "Репортов нет")
    IDEAS = ("ideas_page_number_{current_page}", "ideas_ignore", "Никто не загрузил идеи")

    def __init__(self, page_number_key : str, ignore_key : str, empty_array_text : str) -> None:
        self.page_number_key = page_number_key
        self.ignore_key = ignore_key
        self.empty_array_text = empty_array_text


FASTAPI_URL : str = "http://fastapi:5000"
REQUEST_LIMIT_TTL : int = 60

REPORTS_TIMEOUT : int = 300 # 300 seconds
IDEAS_TIMEOUT : int = 300



REPORT_TEXT : str = """Репорт #{report_id}
@{user_login} (id {user_id}) {report_datetime}
Имя аккаунта {user_fullname}

    {report_text}
"""

IDEA_TEXT : str = """Идея #{idea_id}
@{user_login} (id {user_id}) {idea_datetime}
Имя аккаунта {user_fullname}

    {idea_text}
"""

REPORT_COMMAND_TEXT : str = """💡 *Подсказка* 💡
😊 Для эффективного решения проблемы, просим Вас предоставить файл *DEBUG-LOGS.txt*, находящийся в директории moonloader/config.
📁 Если данного файла нет, активируйте функцию отладки в настройках скрипта и попытайтесь воспроизвести возникшую ошибку.
📝 После этого, детально опишите последовательность действий, приведшую к возникновению проблемы.\n 💡 *Эти действия помогут нам быстрее разобраться с проблемой, хотя они не обязательны* 💡
"""
IDEA_COMMAND_TEXT : str = """
🔍 Пожалуйста, опишите, как именно идея будет работать, для каких целей предназначена и как пользователи смогут её использовать.
"""

WELCOME_TEXT : tuple[str] = ("👋 Добро пожаловать!\n\n""Выберите действие:\n""💸 Купить продукт\n""ℹ️ Узнать информацию о продукте\n""📜 Прочитать лицензионное соглашение\n""📝Написать отчёт о баге (выдача бонусов за важные баги)\n""💡Предложить идею (так же выдача бонусов за интересные идеи)")

INFO_TEXT : str = """🛠️ Скрипт "Tool Of Catcher" (Инструмент для Ловца) 🌟

Скрипт Tool Of Catcher предназначен для игроков на проекте Arizona RP и предлагает целый набор полезных функций, которые сделают ваш игровой процесс проще и приятнее. Идеальный выбор как для новичков, так и для опытных игроков в ловле, которые хотят получать максимум удовольствия от игры! 🚀

🔥 Основные возможности скрипта:
*• Тренировка ввода капчи* 📋
Скрипт предлагает разнообразные режимы тренировки, которые помогут вам улучшить навыки ввода капчи:

🤖 *Соревнования с ботами* 🤖
Режим PayDay 💰 — полная эмуляция реальных условий слёта сезона "скорострелы". Готовьтесь к реальным слётам и повышайте свою реакцию! ⚡
Режим "По Промежуткам" ⏳ — реалистичная симуляция сезона ловли "ловля по инфе". 
Оба этих режима это отличный способ развлечься или соревноваться с ботами! 🤖🏆
Это только описание двух режимов, а в скрипте их еще больше! 😱 

*• Помощь в слётах* 🏠

"Поиск информации" 👁️ —  инструмент с множеством фильтров, позволяющий быстрее и точнее находить нужную информацию о слёте имущества.
Синхронизация промежутков слётов 🌍 — обменивайтесь данными промежутков слётов с другими серверами. Узнавайте, что и когда слетает на других серверах, просто указав это в скрипте.
Запись слётов машин 🚗 — ведите учёт слётов транспорта на своём сервере. Скрипт автоматически сохраняет данные, чтобы вы могли отслеживать, когда и через сколько времени произойдёт следующий слёт транспорта.
Умные оповещения 🔔 — напоминания о важных событиях, таких как PayDay, слёт транспорта или истечение разрешения на ловлю, помогут вам не пропустить ничего важного.

*• Статистика вашей ловли* 📊
Скрипт детально отслеживает вашу игровую статистику, предоставляя информацию о вашем прогрессе:

Личные рекорды по капче и первому символу 🥇.
Среднее время ввода капчи и процент верных попыток 📈.
Визуализация вашего прогресса в удобном формате 🔍. 

*• Полная настройка и кастомизация* 🎨
Скрипт предлагает гибкий и интуитивно понятный интерфейс, позволяющий настроить его под ваши предпочтения:

Изменяйте цвета интерфейса и сообщений для комфортной работы 🌈.
Используйте множество параметров, чтобы адаптировать скрипт именно под ваш стиль игры 🛠️.
✨ И это только начало! ✨
Скрипт Tool Of Catcher содержит множество других полезных функций, которые вы сможете открыть для себя после приобретения. Этот инструмент создан, чтобы сделать вашу игру более удобной и развлекательной.

🛠️ Скрипт использует следующие библиотеки  (зависимости) 📚. Без них его работа будет невозможна:

🎨 mimgui
🪟 MoonMonet
🤣 fAwesome5
🚶‍♂️ lib samp events
⌨️ vkeys
🔧 ffi
🧠 memory
📝 encoding
🔄 effil
⚙️ inicfg
🌐 requests
🪐 moonloader 

👉 Начните использовать Tool Of Catcher и ощутите, насколько проще и интереснее может стать ловля на Arizona RP! 🎮
"""

LICENSE_TEXT : str = """Приобретая данный скрипт (далее – "Продукт"), Вы соглашаетесь с условиями настоящего Пользовательского соглашения:

Отказ от ответственности:
Разработчики Продукта не несут ответственности за блокировку вашего аккаунта, если использование функций Продукта нарушает правила вашего игрового сервера. Все риски, связанные с использованием Продукта, лежат на пользователе.

Право отказа в предоставлении Продукта:
Разработчики оставляют за собой право отказать в продаже Продукта без объяснения причин.

Нарушение лицензионных условий:
Любая попытка взлома, кряка, несанкционированного распространения Продукта или другие подозрительные действия ведут к безвозвратному изъятию лицензии без права на возврат уплаченных средств.

Лицензирование:
Лицензия на использование Продукта выдается только на одно устройство (ПК). Возможность перепривязки лицензии на другое устройство предоставляется на усмотрение разработчиков.

Запрет на модификацию:
Запрещается модификация, декомпиляция, или иное изменение исходного кода Продукта без письменного согласия разработчиков.

Обновления и поддержка:
Разработчики оставляют за собой право вносить изменения и улучшения в Продукт без обязательства предоставлять уведомления пользователям. Поддержка предоставляется на усмотрение разработчиков и может быть прекращена в любой момент.

Конфиденциальность:
Все данные, передаваемые при использовании Продукта, обрабатываются в соответствии с политикой конфиденциальности. Разработчики не передают третьим лицам информацию, связанную с лицензией и личными данными о пользователе/компьютере. Информация не будет разглашена третьим лицам, включая администрацию проекта Arizona RP.

Изменение условий соглашения:
Разработчики оставляют за собой право изменять условия настоящего Пользовательского соглашения. Пользователь обязан самостоятельно отслеживать изменения и соглашаться с ними при продолжении использования Продукта. 

Запрет на передачу:
Пользователь не имеет права передавать, продавать, сдавать в аренду или иным образом предоставлять доступ к Продукту третьим лицам. Данные действия влекут за собой безвозвратному изъятию лицензии без права на возврат уплаченных средств.

Безвозвратность оплаты:
После покупки Продукта возврат уплаченных средств не предусмотрен, независимо от причины отказа от использования или прекращения доступа к Продукту.
"""

BUY_TEXT : str = """🛒 Вы выбрали подписку на скрипт сроком на {duration} месяц(ев).

💳 Для оплаты нажмите на кнопку "Оплатить". После успешного платежа нажмите "Проверить" 🔍, чтобы убедиться, что всё прошло успешно!

⚠️ Перед оплатой обязательно ознакомьтесь с пользовательским соглашением 📜 /license. Мы не несем ответственности, если вы пропустите этот шаг. 
"""
