import os, requests, base64, time, re, sys, subprocess
from datetime import datetime
from dotenv import load_dotenv
import readchar

c = requests.session()
load_dotenv()

class TwitterBot:
    def reply_tweet(self, access, full_reply, tweet_id):
        try:
            dsc = c.get(f"https://ai.relayer.host/tweet/{os.getenv('CLIENT_ID')}/{os.getenv('AI_KEY')}?access_token={access}&text={full_reply}&id={tweet_id}").text
            if('reply.in_reply_to_tweet_id' in dsc):
                print('skipping Community post')
            elif('error' in dsc):
                print(f"Error: {dsc}")
            else:
                print(f"[{datetime.now()}] Berhasil membalas tweet {tweet_id}")
                c.get(f"https://ai.relayer.host/api/user/db/{os.getenv('AI_KEY')}?done={tweet_id}").json()
                time.sleep(20)
        except Exception as e:
            pass

def update_refresh_token(new_token):
    lines = []
    found = False
    if not os.path.exists(".env"):
        lines = [f"REFRESH_TOKEN={new_token}\n"]
    else:
        with open(".env", 'r') as f:
            for line in f:
                if line.startswith("REFRESH_TOKEN="):
                    lines.append(f"\nREFRESH_TOKEN={new_token}\n")
                    found = True
                else:
                    lines.append(line)
        if not found:
            lines.append(f"REFRESH_TOKEN={new_token}")
    with open(".env", 'w') as f:
        f.writelines(lines)
    load_dotenv(override=True)

def login():
    url = f"https://ai.relayer.host/authorize?cid={os.getenv('CLIENT_ID')}"
    if sys.platform == "win32":
        os.system(f'start {url}')
    else:
        print(f"https://ai.relayer.host/authorize?cid={os.getenv('CLIENT_ID')}")
        input("Press Enter to input token")

def get_new_token():
    tok = c.get(f"https://ai.relayer.host/refresh_token?refresh={os.getenv('REFRESH_TOKEN')}&cid={os.getenv('CLIENT_ID')}").json()
    update_refresh_token(tok['refresh_token'])
    return tok['access_token']

def is_already_done(tweet_id):
    ds = c.get(f"https://ai.relayer.host/api/user/db/{os.getenv('AI_KEY')}").json()
    if 'done' in ds and str(tweet_id) in ds['done']:
        return True
    else:
        return False

def get_tid(user):
    ids = c.get(f"https://ai.relayer.host/api/getid/{os.getenv('AI_KEY')}?username={user.replace('@','')}").json()['user_id']
    time.sleep(5)
    return ids

def extract_url(input_text):
    pattern = r"https://x.com/[^/]+/status/\d+"
    urls = re.findall(pattern, input_text)
    return urls

def extract_id(url):
    pattern = r"https://x.com/([^/]+)/status/(\d+)"
    match = re.search(pattern, url)
    if match:
        username = match.group(1)
        tweet_id = match.group(2)
        return username, tweet_id
    else:
        print(f"No match found for URL: {url}")
        return None, None

def get_twit(user, projects, skip_check):
    responsed = c.get(f"https://ai.relayer.host/api/tweet/{os.getenv('AI_KEY')}?id={user}").json()
    if responsed['status'] == "Failed":
        return None, None
    text = base64.b64decode(responsed['text']).decode('utf-8')
    tweet_id = responsed['tweet_id']
    if is_already_done(tweet_id):
        print(f"Tweet {tweet_id} sudah pernah direply, skip.")
        return None, None
    if not text or not tweet_id:
        return None, None
    projects_list = [p.strip().lower() for p in projects.split(',')]
    text_lower = text.lower()
    for project in projects_list:
        if project in text_lower:
            response = c.get(f"https://ai.relayer.host/api/{os.getenv('AI_KEY')}?text={text}")
            if(response.status_code != 200):
                sys.exit(f"Rate Limit Exceeded from AI")
            response_json = response.json()
            decoded_msg = (base64.b64decode(response_json['message']).decode('utf-8'))
            print(f"Tweet: {text}")
            print("=" * 100 + "\n")
            print(f"Reply: {decoded_msg}")
            print("=" * 100 + "\n")
            if skip_check == True:
                return tweet_id, decoded_msg
            else:
                user_input = input("Apakah reply akan di edit? (Y/N): ").lower()
                if user_input == "y":
                    message = input("Masukkan reply baru: ")
                else:
                    message = decoded_msg
                return tweet_id, message
    return None, None


def raid(id, skip_check):
    responsed = c.get(f"https://ai.relayer.host/api/user/tweet/{os.getenv('AI_KEY')}?tweet={id}").json()
    if responsed['status'] == "Failed":
        return None, None
    text = base64.b64decode(responsed['text']).decode('utf-8')
    tweet_id = responsed['tweet_id']
    if is_already_done(tweet_id):
        print(f"Tweet {tweet_id} sudah pernah direply, skip.")
        return None, None
    if not text or not tweet_id:
        return None, None
    response = c.get(f"https://ai.relayer.host/api/{os.getenv('AI_KEY')}?text={text}")
    if(response.status_code != 200):
        sys.exit(f"Rate Limit Exceeded from AI")
    response_json = response.json()
    decoded_msg = (base64.b64decode(response_json['message']).decode('utf-8')).replace('.','')
    print(f"Tweet: {text}")
    print("=" * 100 + "\n")
    print(f"Reply: {decoded_msg}")
    print("=" * 100 + "\n")
    if skip_check == True:
        return tweet_id, decoded_msg
    else:
        user_input = input("Apakah reply akan di edit? (Y/N): ").lower()
        if user_input == "y":
            message = input("Masukkan reply baru: ")
        else:
            message = decoded_msg
            return tweet_id, message
        
def melon_raid(bot):
    load_dotenv()
    usern = c.get(f"https://ai.relayer.host/api/user/db/{os.getenv('AI_KEY')}").json()['X']
    myacc = usern.lower()
    token = get_new_token()
    list = c.get(f"https://ai.relayer.host/melon/raid/{os.getenv('AI_KEY')}").json()
    if(list == []):
        print("Ai key Tidak Valid")
    else:
        for url in list:
            user, ids = extract_id(url)
            try:
                if(myacc == user.lower()):
                    continue
                print(f"Otw raid @{user} Tweet {ids}")
                if is_already_done(ids):
                    print(f"Tweet {ids} dari @{user} sudah pernah direply, skip.")
                    continue
                try:
                    ids, reply_text = raid(ids, True)
                except Exception:
                    time.sleep(5)
                    ids, reply_text = raid(ids, True)
                try:
                    bot.reply_tweet(token, reply_text, ids)
                except Exception:
                    print("Retry Reply")
                    bot.reply_tweet(token, reply_text, ids)
            except Exception as e:
                time.sleep(5)
                print(f"Error pada username @{user}: {e}")
        print("Doneeee semua serrr")

def auto_raid(bot):
    token = get_new_token()
    listny = input("List Targetnya: ")
    opsi = input("skip crosscheck reply? (Y/N): ").lower()
    if opsi == "y":
        skip_check = True
    else:
        skip_check = False
    urls = extract_url(listny)
    for url in urls:
        user, ids = extract_id(url)
        try:
            print(f"Target: @{user} and Tweet: {ids}")
            if is_already_done(ids):
                print(f"Tweet {ids} dari @{user} sudah pernah direply, skip.")
                continue
            ids, reply_text = raid(ids, skip_check)
            try:
                bot.reply_tweet(token, reply_text, ids)
            except Exception:
                print("Retry Reply")
                bot.reply_tweet(token, reply_text, ids)
        except Exception as e:
            print(f"Error pada username @{user}: {e}")
    input("Enter untuk kembali ke menu")

def reply_twit(bot, usernames):
    projects = input("Project (Example: caldera, memex): ")
    opsi = input("skip crosscheck reply? (Y/N): ").lower()
    if opsi == "y":
        skip_check = True
    else:
        skip_check = False
    while True:
        token = get_new_token()
        for username in usernames:
            try:
                username = username.replace('@', '')
                print(f"target: {username}")
                user_id = get_tid(username.lower())
                if user_id is None or user_id is None:
                    print(f"User @{username} tidak ditemukan, skip.")
                    continue
                id, reply_text = get_twit(user_id, projects, skip_check)
                if id is None:
                    print(f"Tidak Ada Tweet Yang memenuhi Filter untuk @{username}")
                    continue
                if is_already_done(id):
                    print(f"Tweet {id} dari @{username} sudah pernah direply, skip.")
                    continue
                try:
                    bot.reply_tweet(token, reply_text, id)
                except Exception:
                    print("Retry Reply")
                    bot.reply_tweet(token, reply_text, id)
            except Exception as e:
                    print(f"Error pada username @{username}: {e}")
        print("Selesai, tunggu 3 jam untuk melanjutkan.")
        time.sleep(10800)

def simple_menu(options):
    idx = 0
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=== Twitter Auto Reply Bot ===\nGithub: JustPandaEver\nX: PandaEverX\n")
        for i, option in enumerate(options):
            if i == idx:
                print(f"=> {option}")
            else:
                print(f"  {option}")
        key = readchar.readkey()
        if key == readchar.key.UP:
            idx = (idx - 1) % len(options)
        elif key == readchar.key.DOWN:
            idx = (idx + 1) % len(options)
        elif key == readchar.key.ENTER or key == '\r':
            return idx


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    bot = TwitterBot()
    with open("target.txt", "r") as f:
        usernames = [line.strip() for line in f if line.strip()]
    menu_options = [
        "Reply tweet",
        "Melon Full Auto Raid",
        "Auto Raid",
        "Exit"
    ]
    while True:
        choice = simple_menu(menu_options)
        print(f"Kamu memilih: {menu_options[choice]}")
        if choice == 0:
            reply_twit(bot, usernames)
        elif choice == 1:
            melon_raid(bot)
        elif choice == 2:
            auto_raid(bot)
        elif choice == 3:
            print("Keluar dari program.")
            break

if __name__ == "__main__":
    if(os.getenv('REFRESH_TOKEN') == None or os.getenv('REFRESH_TOKEN') =='\n' or os.getenv('REFRESH_TOKEN') ==''):
        login()
        the_token = input("Refresh Token? ")
        update_refresh_token(the_token)
    load_dotenv(override=True)
    main()
