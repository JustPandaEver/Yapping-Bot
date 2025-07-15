import os, requests, base64, time, re, hashlib, sys, subprocess, shutil, tempfile
from datetime import datetime
from dotenv import load_dotenv
c = requests.session()
load_dotenv()


class TwitterBot:
    def reply_tweet(self, access, full_reply, tweet_id):
        try:
            dsc = c.get(f"https://ai.relayer.host/tweet?access_token={access}&text={full_reply}&id={tweet_id}").text
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
                    lines.append(f"REFRESH_TOKEN={new_token}\n")
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
        os.system(f'xdg-open {url}')

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
            response = c.get(f"https://ai.relayer.host/api/{os.getenv('AI_KEY')}?text={text}").json()
            decoded_msg = (base64.b64decode(response['message']).decode('utf-8'))
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
    response = c.get(f"https://ai.relayer.host/api/{os.getenv('AI_KEY')}?text={text}").json()
    decoded_msg = (base64.b64decode(response['message']).decode('utf-8'))
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

def get_file_sha256(file_path):
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def check_update_with_temp_clone():
    try:
        temp_dir = tempfile.mkdtemp()
        result = subprocess.run(
            ["git", "clone", "--depth", "1", "https://github.com/JustPandaEver/Yapping-Bot.git", temp_dir],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print("Gagal clone repo:")
            print(result.stderr)
            shutil.rmtree(temp_dir)
            return
        temp_main = os.path.join(temp_dir, "main.py")
        if not os.path.exists(temp_main):
            print("main.py tidak ditemukan di repo!")
            shutil.rmtree(temp_dir)
            return
        local_hash = get_file_sha256(__file__)
        temp_hash = get_file_sha256(temp_main)

        print(f"SHA256 lokal: {local_hash}")
        print(f"SHA256 repo : {temp_hash}")
        if local_hash == temp_hash:
            print("Sudah menggunakan versi terbaru.")
        else:
            print("Ada update terbaru di repo!")
            sys.exit()
    except Exception as e:
        print(f"Error saat cek update: {e}")


def main():
    print("=== Twitter Auto Reply Bot ===\nGithub: JustPandaEver\nX: PandaEverX\n")
    bot = TwitterBot()
    with open("target.txt", "r") as f:
        usernames = [line.strip() for line in f if line.strip()]
    while True:
        print("1. Reply tweet\n2. Melon Full Auto Raid\n3. Auto Raid\n4. Cek Update\n5. Keluar")
        choices = str(input("Pilih menu: "))
        if choices == "1":
            reply_twit(bot, usernames)
        elif choices == "2":
            melon_raid(bot)
        elif choices == "3":
            auto_raid(bot)
        elif choices == "4":
            check_update_with_temp_clone()
        elif choices == "5":
            print("Keluar dari program.")
            break            
        else:
            print("Pilihan tidak valid.")

if __name__ == "__main__":
    if(os.getenv('REFRESH_TOKEN') == None or os.getenv('REFRESH_TOKEN') =='\n' or os.getenv('REFRESH_TOKEN') ==''):
        login()
        the_token = input("Refresh Token? ")
        update_refresh_token(the_token)
    load_dotenv(override=True)
    main()
