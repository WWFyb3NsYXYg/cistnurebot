import os
import requests

isFirst = True

def getGroups(isFirst):
    global groups_info
    if isFirst:
        response = requests.get('https://cist.nure.ua/ias/app/tt/P_API_GROUP_JSON')
        response.raise_for_status()  
        groups_info = response.json()
        isFirst = False 
    return groups_info
    
def find_group_id(response, group_name):
    for faculty in response.get("university", {}).get("faculties", []):
        for direction in faculty.get("directions", []):
            for speciality in direction.get("specialities", []):
                for group in speciality.get("groups", []):
                    if group.get("name") == group_name:
                        return group.get("id")
    return None

def Info():
    try:
            
        response = requests.get(CIST_URL)
        response.raise_for_status() 
        cist_info = response.json() 
        return cist_info
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    
     

            
API_TOKEN = input("Введіть API токен Telegram (отримати https://t.me/botfather): ")


while True:
    GROUP_NAME = str(input("\nВведіть назву групи (наприклад, ІСТ-22-1): "))
    group_id = find_group_id(getGroups(isFirst), GROUP_NAME)
    if group_id is not None:
        NURE_GROUP_ID = group_id
        break
    else:
        print(f"\nГруппа {GROUP_NAME} не знайдено. Повторення...")
    
CIST_URL = 'https://cist.nure.ua/ias/app/tt/P_API_EVEN_JSON?type_id=1&timetable_id='+ str(NURE_GROUP_ID) +'&idClient=KNURESked'
channel_id = input("Введіть ID каналу, в який за розкладом будуть надходити повідомлення, починається на -100ХХХХХХХХХХ (отримати ID каналу можна переславши повідомлення з нього в бот https://t.me/getmyid_bot): ")
user_input = input("\nВведіть IDшники авторизованих користувачів, через кому БЕЗ ПРОБІЛІВ, отримати їх можна так само через бота https://t.me/getmyid_bot переславши йому повідомлення від цього користувача: ")
authorized_users = [int(user_id) for user_id in user_input.split(",")]
data = Info()
urls = {}
for subject in data["subjects"]:
    subject_id = subject["id"]
    subject_title = subject["brief"]
    teachers_data = subject["hours"]
    teacher_set = set() 
    teacher_urls = []
    for hour in teachers_data:
        for teacher_id in hour["teachers"]:
            if teacher_id not in teacher_set:
                teacher_name = next((t["short_name"] for t in data["teachers"] if t["id"] == teacher_id), "")
                print ('\nПосилання мають бути у форматі https://meet.google.com/xxx-xxxx-xxx. \n\nВводити потрібно лише код зустрічі у форматі xxx-xxxx-xxx')
                teacher_url = str(input("Введіть код зустрічі для" + teacher_name + " "+ subject_title+": ")) 
                teacher_set.add(teacher_id)
                teacher_urls.append({teacher_id: teacher_url})
                urls[subject_id] = teacher_urls
                

                
with open("config.py", "w", encoding="utf-8") as f:
    f.write(f"API_TOKEN = '{API_TOKEN}'\n")
    f.write(f"GROUP_NAME = '{GROUP_NAME}'\n")
    f.write(f"NURE_GROUP_ID = '{NURE_GROUP_ID}'\n")
    f.write(f"channel_id = '{channel_id}'\n")
    f.write(f"authorized_users = {authorized_users}\n")
    f.write(f"urls = {urls}\n")

print("\nФайл config.py згенеровано успішно!")
