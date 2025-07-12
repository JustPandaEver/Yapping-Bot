import os, tweepy, requests, base64, time, re, hashlib, sys, subprocess, shutil, tempfile
from datetime import datetime
from dotenv import load_dotenv
import tweepy.errors
c = requests.session()
load_dotenv()

def countdown_display(total_seconds, message="Rate Limit Exceeded, waiting"):
    for remaining in range(total_seconds, 0, -1):
        minutes = remaining // 60
        seconds = remaining % 60
        countdown_text = f"{message} {remaining} seconds until reset! ({minutes:02d}:{seconds:02d})"
        print(f"\r{countdown_text}", end="", flush=True)
        time.sleep(1)
    print()

class TwitterBot:
    def __init__(self):
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.client = tweepy.Client(
            bearer_token=self.bearer_token,
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
            wait_on_rate_limit=False)
        
    def reply_tweet(self, full_reply, tweet_id):
        try:
            self.client.create_tweet(
                text=full_reply,
                in_reply_to_tweet_id=tweet_id
            )            
            print(f"[{datetime.now()}] Berhasil membalas tweet {tweet_id}")
            with open("done.txt", "a") as f:
                f.write(f"{tweet_id}\n")
        except tweepy.errors.HTTPException as e:
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 429:
                    reset_time = e.response.headers.get('x-rate-limit-reset')
                    if reset_time:
                        import time
                        current_time = int(time.time())
                        wait_time = int(reset_time) - current_time + 30
                        if wait_time > 0:
                            countdown_display(wait_time, "Rate Limit Exceeded, waiting")
                        else:
                            countdown_display(60, "Rate Limit Exceeded, waiting")
                    else:
                        countdown_display(900, "Rate Limit Exceeded, waiting")
                    self.reply_tweet(full_reply, tweet_id)
                elif e.response.status_code == 403:
                    print("Forbidden: Tweet mungkin sudah dihapus atau apikey twiter di .env salah")
                elif e.response.status_code == 404:
                    print("Tweet tidak ditemukan")
                else:
                    print(f"HTTP Error {e.response.status_code}: {e}")
            else:
                print(f"HTTPException: {e}")
        except Exception as e:
            print(f"Error membalas tweet: {e}")

    def follow_user(self, userid=None):
        try:
            self.client.follow_user(target_user_id=userid)
        except tweepy.errors.HTTPException as e:
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 429:
                    reset_time = e.response.headers.get('x-rate-limit-reset')
                    if reset_time:
                        import time
                        current_time = int(time.time())
                        wait_time = int(reset_time) - current_time + 30
                        if wait_time > 0:
                            countdown_display(wait_time, "Rate Limit Exceeded, waiting")
                        else:
                            countdown_display(60, "Rate Limit Exceeded, waiting")
                    else:
                        countdown_display(900, "Rate Limit Exceeded, waiting")
                    self.follow_user(userid)
                elif e.response.status_code == 403:
                     print("Forbidden: apikey twiter di .env salah")
                elif e.response.status_code == 404:
                    print("User tidak ditemukan")
                else:
                    print(f"HTTP Error {e.response.status_code}: {e}")
            else:
                print(f"HTTPException: {e}")
        except Exception as e:
            print(f"Error follow: {e}")

    def get_current_username(self):
        try:
            user = self.client.get_me().data
            if user:
                print(f"Username akun saat ini: @{user.username}\n")
                return user.username
            else:
                print("Gagal mendapatkan informasi user.")
                return None
        except Exception as e:
            sys.exit("Pastikan isi Twitter apikey di .env benar")

def is_already_done(tweet_id):
    if not os.path.exists("done.txt"):
        return False
    with open("done.txt", "r") as f:
        done_ids = f.read().splitlines()
    return str(tweet_id) in done_ids

def get_tid(user):
    ids = c.get(f"https://ai.relayer.host/api/getid/{os.getenv('AI_KEY')}?username={user.replace('@','')}").json()['user_id']
    time.sleep(5)
    return ids

def is_already_followed(username):
    if not os.path.exists("followed.txt"):
        return False
    with open("followed.txt", "r") as f:
        followed_names = f.read().splitlines()
    return username.lower() in [u.lower() for u in followed_names]

def save_followed(username):
    with open("followed.txt", "a") as f:
        f.write(f"{username}\n")

def follow_all_targets(bot, usernames):
    for username in usernames:
        try:
            username = username.replace('@', '')
            print(f"target: @{username}")
            if is_already_followed(username):
                print(f"User @{username} sudah pernah di-follow, skip follow.")
                continue
            user_id = get_tid(username.lower())
            if user_id is None or user_id is None:
                print(f"User @{username} tidak ditemukan, skip.")
                continue
            try:
                bot.follow_user(user_id)
            except Exception:
                print("Retry Follow")
                bot.follow_user(user_id)
            save_followed(username)
            print(f"Berhasil follow @{username} dan simpan ke followed.txt")
        except Exception as e:
            print(f"Error pada username @{username}: {e}")

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
        
def melon_raid(bot, self_acc):
    myacc = self_acc.lower().replace('@','')
    while True:
        list = c.get(f"https://ai.relayer.host/melon/raid/{os.getenv('AI_KEY')}").json()
        if(list == []):
            print("Ai key Tidak Valid")
        else:
            for url in list:
                user, ids = extract_id(url)
                try:
                    if(myacc == user):
                        continue
                    print(f"Otw raid @{user} Tweet {ids}")
                    if is_already_done(ids):
                        print(f"Tweet {ids} dari @{user} sudah pernah direply, skip.")
                        continue
                    ids, reply_text = raid(ids, True)
                    try:
                        bot.reply_tweet(reply_text, ids)
                    except Exception:
                        print("Retry Reply")
                        bot.reply_tweet(reply_text, ids)
                except Exception as e:
                    print(f"Error pada username @{user}: {e}")
            time.sleep(20)
        print("Cycle Sudah selesai, tunggu 5 menit sebelum otomatis mengulang cycle")
        time.sleep(300)
        

def auto_raid(bot):
    listny = input("List Targetnya: ")
    opsi = input("skip crosscheck reply? (Y/N): ").lower()
    follow = input("check and auto follow user? (Y/N): ").lower()
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
                bot.reply_tweet(reply_text, ids)
            except Exception:
                print("Retry Reply")
                bot.reply_tweet(reply_text, ids)
            if(follow == "y"):
                if is_already_followed(user):
                    print(f"User @{user} sudah pernah di-follow, skip follow.")
                    continue
                print(f"target: {user}")
                try:
                    user_id = get_tid(user.lower())
                    bot.follow_user(user_id)
                    save_followed(user)
                    print(f"Berhasil follow @{user} dan simpan ke followed.txt")
                except Exception:
                    print(f"Gagal Auto Follow @{user}")
        except Exception as e:
            print(f"Error pada username @{user}: {e}")
        time.sleep(20)

def reply_twit(bot, usernames):
    projects = input("Project (Example: caldera, memex): ")
    opsi = input("skip crosscheck reply? (Y/N): ").lower()
    follow = input("check and auto follow user? (Y/N): ").lower()
    if opsi == "y":
        skip_check = True
    else:
        skip_check = False
    while True:
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
                    bot.reply_tweet(reply_text, id)
                except Exception:
                    print("Retry Reply")
                    bot.reply_tweet(reply_text, id)
                if(follow == "y"):
                    if is_already_followed(username):
                        print(f"User @{username} sudah pernah di-follow, skip follow.")
                        continue
                    bot.follow_user(user_id)
                    save_followed(username)
                    print(f"Berhasil follow @{username} dan simpan ke followed.txt")
                time.sleep(20)
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
            print("Mengambil main.py terbaru dan replace file lokal...")
            with open(temp_main, "r", encoding="utf-8") as src, open(__file__, "w", encoding="utf-8") as dst:
                dst.write(src.read())
            print("main.py berhasil diupdate! Silakan restart program.")
            sys.exit()
    except Exception as e:
        print(f"Error saat cek update: {e}")

def main():
    print("=== Twitter Auto Reply Bot ===\nGithub: JustPandaEver\nX: PandaEverX\n")
    bot = TwitterBot()
    usern = bot.get_current_username()
    with open("target.txt", "r") as f:
        usernames = [line.strip() for line in f if line.strip()]
    while True:
        print("1. Follow semua target\n2. Reply tweet\n3. Melon Full Auto Raid\n4. Auto Raid\n5. Cek Update\n6. Keluar")
        choices = str(input("Pilih menu: "))
        if choices == "1":
            follow_all_targets(bot, usernames)
        elif choices == "2":
            reply_twit(bot, usernames)
        elif choices == "3":
            melon_raid(bot, usern)
        elif choices == "4":
            auto_raid(bot)
        elif choices == "5":
            check_update_with_temp_clone()
        elif choices == "6":
            print("Keluar dari program.")
            break
        else:
            print("Pilihan tidak valid.")

if __name__ == "__main__":
    main()
