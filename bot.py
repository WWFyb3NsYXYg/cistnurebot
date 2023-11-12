# ================================================================================================================================================================
# ================================================================ FOR DEVELOPERS ================================================================================
# ================================================================================================================================================================

offset = 7200 #utc+2 часовой пояс, еще не разобрался, пока +2, летом +3(наверное)

import time, requests, asyncio, aioschedule
from datetime import datetime, timezone, timedelta
from aiogram import Bot, Dispatcher, types, executor
try:
    import config
    print("Модуль конфігурації успішно імпортовано.")
except ImportError:
    print("Помилка: не можна імпортувати модуль «config».")
    print("Будь ласка, запустіть скрипт «gen_file.py», щоб створити файл конфігурації».")
    exit(1)
    

last_request_time = 0

work_day = True 

CIST_URL = 'https://cist.nure.ua/ias/app/tt/P_API_EVEN_JSON?type_id=1&timetable_id='+ config.NURE_GROUP_ID +'&idClient=KNURESked'

bot = Bot(token=config.API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

def Info():
    global last_request_time
    global cist_info 
    current_time = time.time()
    time_diff = current_time - last_request_time
    if time_diff > 300:     # Если прошло менее 300 секунд с последнего вызова, игнорируем команду
        last_request_time = current_time
        try:
            response = requests.get(CIST_URL)
            response.raise_for_status()  # Check for any HTTP request errors
            cist_info = response.json()  # Parse the JSON response

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
    else:
        print(
            f"Command execution limit exceeded. Please wait {round(300 - time_diff)} sec.")
    
    return cist_info 

def pharse(cist_info, day):
    current_date = datetime.now(timezone.utc).astimezone(timezone.utc).date()
    if day == 'now':
        None     
    else:
        current_date = day
        
    print_date = current_date.strftime("%d.%m.%Y")  
    markup = types.InlineKeyboardMarkup()
    send_text = f'Розклад на {print_date}\n\n'
    work_day = False
    for event in cist_info['events']:
        teachers = cist_info['teachers']
        subjects = cist_info['subjects']
        typeN = cist_info['types']
        start_time = time.strftime("%H:%M", time.gmtime(event["start_time"]+offset))
        end_time = time.strftime("%H:%M", time.gmtime(event["end_time"]+offset))
        event_date = datetime.fromtimestamp(event["start_time"]).date()
        if event_date == current_date:
            work_day = True
            subject_id = event['subject_id']
            #number_pair = event["number_pair"]
            #auditory = event["auditory"]
            teacher_ids = event['teachers']
            #group_ids = event["groups"]
            event_type = event['type']
            subject = next(subj for subj in subjects if subj["id"] == subject_id)
            subject_title = subject['title']  
            short_subject_title = subject['brief']
            teacher_names = [teacher['short_name'] for teacher in teachers if teacher['id'] in teacher_ids]
            #group_names = [group["name"] for group in groups if group["id"] in group_ids]
            event_type_name = next(t['full_name'] for t in typeN if t['id'] == event_type)
            
            
            teacher_url = None  # Default to None
            for inner_dict in config.urls.get(subject_id, []):
                for teacher_id, url in inner_dict.items():
                    if teacher_id in teacher_ids:
                        teacher_url = "https://meet.google.com/" + url
                        button = types.InlineKeyboardButton(text='🔗 ' + short_subject_title + ' (' + teacher_names[0] + ')', url = teacher_url)
                        markup.add(button) 
                       
            send_text += f"💼 {subject_title} ({event_type_name})\n🕖Час: {start_time} - {end_time}\n👩‍🏫 Викладач: {', '.join(teacher_names)}\n\n"
    if work_day == False:
        send_text += f"Пар нема)"    
    return send_text, markup, work_day
       
async def schedule_print():
    result = pharse(Info(), 'now')
    if result[2]: # если в расписании есть предметы
        await bot.send_message(config.channel_id, result[0], reply_markup=result[1])
    else:
        print("Сьогодні пар нема)")

async def scheduler():
    aioschedule.every().day.at("07:30").do(schedule_print)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def on_startup(_):
    asyncio.create_task(scheduler())

@dp.inline_handler()
async def on_inline_query(inline_query: types.InlineQuery):
    chat_id = inline_query.from_user.id
    query_text = inline_query.query

    if chat_id in config.authorized_users:
        current_datetime = datetime.now()
        current_year = current_datetime.year
        date_format = "%d.%m"  
        try:
            
            query_date = datetime.strptime(query_text, date_format).date()
            query_date = query_date.replace(year=current_year)
            if query_date < current_datetime.date():
                query_date = query_date.replace(year=current_year+1)
            result = pharse(Info(), query_date)
            title = f'Розклад групи {config.GROUP_NAME} на {query_date.strftime("%d.%m.%Y")}'
        except ValueError:
            result = pharse(Info(), 'now')
            title = f'Розклад групи {config.GROUP_NAME} на сьогодні'

        item = types.InlineQueryResultArticle(
            id='1',
            title=title,
            
            description='Натисніть, щоб відправити це повідомлення через мене',
            input_message_content=types.InputTextMessageContent(
                message_text=result[0]
            ),
            reply_markup=result[1],
            thumb_url = 'https://ysc.nure.ua/wp-content/uploads/2023/05/Logo_nure.png'
        )

        await bot.answer_inline_query(inline_query.id, results=[item], cache_time=0)
 
 
         
@dp.message_handler(commands=['schedule'])
async def on_schedule_command(message: types.Message):
    chat_id = message.chat.id
    if chat_id in config.authorized_users:
        # Извлекаем текст сообщения пользователя после команды /schedule
        command_args = message.get_args()

        # Проверяем, была ли введена дата после команды
        if command_args:
            try:
                current_datetime = datetime.now()
                current_year = current_datetime.year
                schedule_date = datetime.strptime(command_args, "%d.%m")
                schedule_date = schedule_date.replace(year=current_year)
                if schedule_date.date() < current_datetime.date(): # if date is in past
                    schedule_date = schedule_date.replace(year=current_year+1)
                    
                
                result = pharse(Info(), schedule_date.date())
                
            except ValueError:
                await message.reply('Неправильний формат дати. Використовуйте DD.MM\nВведіть дату після команди. Наприклад, `/schedule 07.11`', parse_mode = 'Markdown')
        else:
            result = pharse(Info(), 'now')
            
        await message.reply(result[0], reply_markup=result[1])
        
@dp.message_handler(commands=['update'])
async def upd_channel(message: types.Message):
    chat_id = message.chat.id
    if chat_id in config.authorized_users:
        result = pharse(Info(), 'now')
        await bot.send_message(config.channel_id, result[0], reply_markup=result[1])
        await message.reply("Розклад було надіслано до каналу ✅")

        
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)