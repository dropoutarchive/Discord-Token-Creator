import os
import time
import random
import logging
import requests
import websocket
import threading
from json import dumps
from getpass import getpass
from capmonster_python import HCaptchaTaskProxyless

logging.basicConfig(
    level=logging.INFO,
    format="\u001b[36;1m[\u001b[0m\033[4mdropout.black\033[0m\u001b[36;1m]\u001b[0m %(message)s\u001b[0m"
)

class Discord:

    def __init__(self, apikey, proxy):
        with open("data/proxies.txt", encoding="utf-8") as f:
            self.proxies = [i.strip() for i in f]

        self.proxy = proxy

        self.apikey = apikey
        self.user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.0.16 Chrome/91.0.4472.164 Electron/13.4.0 Safari/537.36"

        self.base_url = "https://discord.com/"
        self.sitekey = "f5561ba9-8f1e-40ca-9b5b-a0b3f719ef34"

        self.captcha = HCaptchaTaskProxyless(
            client_key=self.apikey,
            userAgent=self.user_agent
        )

        self.headers = {
            "Host": "discord.com",
            "Connection": "keep-alive",
            "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzkzLjAuNDU3Ny42MyBTYWZhcmkvNTM3LjM2IEVkZy85My4wLjk2MS40NyIsImJyb3dzZXJfdmVyc2lvbiI6IjkzLjAuNDU3Ny42MyIsIm9zX3ZlcnNpb24iOiIxMCIsInJlZmVycmVyIjoiaHR0cHM6Ly9kaXNjb3JkLmNvbS9jaGFubmVscy81NTQxMjU3Nzc4MTg2MTU4NDQvODcwODgxOTEyMzQyODUxNTk1IiwicmVmZXJyaW5nX2RvbWFpbiI6ImRpc2NvcmQuY29tIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjk3NTA3LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==",
            "X-Fingerprint": "",
            "Accept-Language": "en-US",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.47",
            "Content-Type": "application/json",
            "Authorization": "undefined",
            "Accept": "*/*", "Origin": "https://discord.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://discord.com/register",
            "X-Debug-Options": "bugReporterEnabled",
            "Accept-Encoding": "gzip, deflate, br",
            "Cookie": "OptanonConsent=version=6.17.0; locale=th"
        }

    def _get_captcha(self):
        task_id = self.captcha.createTask(
            website_url=self.base_url,
            website_key=self.sitekey
        )
        logging.info("Created task (\u001b[36;1m%s\u001b[0m)" % (task_id))
        try:
            result = self.captcha.joinTaskResult(
                taskId=task_id
            )
            if result != None:
                logging.info("Solved captcha (\u001b[36;1m%s\u001b[0m)" % (result[:54]))
                return result
            else:
                logging.info("Failed to solve captcha, retrying...")
                return self._get_captcha()
        except Exception:
            logging.info("Failed to solve captcha, retrying...")
            return self._get_captcha()

    def _websocket_connect(self, token):
        ws = websocket.WebSocket()
        ws.connect("wss://gateway.discord.gg/?encoding=json&v=9&compress=zlib-stream")
        logging.info("Connected to gateway v9 (\u001b[36;1m%s%s\u001b[0m)" % (token[:32], "*"*27))
        ws.send("{\"op\":2,\"d\":{\"token\":\"%s\",\"capabilities\":125,\"properties\":{\"os\":\"Windows\",\"browser\":\"Chrome\",\"device\":\"\",\"system_locale\":\"it-IT\",\"browser_user_agent\":\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36\",\"browser_version\":\"91.0.4472.124\",\"os_version\":\"10\",\"referrer\":\"\",\"referring_domain\":\"\",\"referrer_current\":\"\",\"referring_domain_current\":\"\",\"release_channel\":\"stable\",\"client_build_number\":89709,\"client_event_source\":null},\"presence\":{\"status\":\"online\",\"since\":0,\"activities\":[],\"afk\":false},\"compress\":false,\"client_state\":{\"guild_hashes\":{},\"highest_last_message_id\":\"0\",\"read_state_version\":0,\"user_guild_settings_version\":-1}}}" % (token))
        logging.info("Sent connect payload (\u001b[36;1m%s%s\u001b[0m)" % (token[:32], "*"*27))
        ack = {
            "op": 1,
            "d": None
        }
        ws.send(dumps(ack))
        logging.info("Sent heartbeat (\u001b[36;1m%s%s\u001b[0m)" % (token[:32], "*"*27))

        for x in range(15):
            time.sleep(35)
            try:
                ws.send(dumps(ack))
                logging.info("Sent heartbeat %s (\u001b[36;1m%s%s\u001b[0m)" % (x+1, token[:32], "*"*27))
            except Exception:
                break

        ws.close()
        logging.info("Closed websocket connection (\u001b[36;1m%s%s\u001b[0m)" % (token[:32], "*"*27))

    def _create_account(self, invite, captcha = None):
        json = {
            "username": "dropout",
            "password": os.urandom(15).hex(),
            "email": "%s@dropout.black" % (os.urandom(15).hex()),
            "invite": invite,
            "consent": True
        }

        if captcha == None:
            json["captcha_key"] = self._get_captcha()
        else:
            json["captcha_key"] = captcha

        if self.proxy["enabled"]:
            proxies = {"https": "%s://%s" % (self.proxy["type"], random.choice(self.proxies))}
        else:
            proxies = None

        try:
            r = requests.post("https://discord.com/api/v9/auth/register", json=json, headers=self.headers, proxies=proxies, timeout=5)
            if r.status_code in (200, 201, 204):
                token = r.json()["token"]
                logging.info("Created account (\u001b[36;1m%s%s\u001b[0m)" % (token[:32], "*"*27))
                with open("data/tokens.txt", "a+") as f:
                    f.write("%s:%s\n" % (token, json["password"]))
                    f.close()
                threading.Thread(target=self._websocket_connect, args=(token,)).start()
            elif "You are being rate limited." in r.text:
                retry_after = r.json()["retry_after"]
                logging.info("Failed to create account. (\u001b[36;1mratelimit for %s\u001b[0m)" % (retry_after))
                time.sleep(retry_after)
                self._create_account(invite, json["captcha_key"])
            else:
                logging.info("Failed to create account. (\u001b[36;1maccount_failure\u001b[0m)")
                self._create_account(invite, json["captcha_key"])
        except Exception:
            logging.info("Failed to create account. (\u001b[36;1mproxy_failure\u001b[0m)")
            self._create_account(invite, json["captcha_key"])

if __name__ == "__main__":
    threads = []

    client = Discord(
        apikey=getpass(prompt="\u001b[36;1m[\u001b[0m\033[4mdropout.black\033[0m\u001b[36;1m]\u001b[0m ApiKey (\u001b[36;1mcapmonster.cloud\u001b[0m) \u001b[36;1m->\u001b[0m "),
        proxy={
            "enabled": True,
            "type": input("\u001b[36;1m[\u001b[0m\033[4mdropout.black\033[0m\u001b[36;1m]\u001b[0m Proxy type (\u001b[36;1mhttp/socks4/socks5\u001b[0m) \u001b[36;1m->\u001b[0m ")
        }
    )

    invite = input("\u001b[36;1m[\u001b[0m\033[4mdropout.black\033[0m\u001b[36;1m]\u001b[0m Invite \u001b[36;1m->\u001b[0m discord.gg/")
    amount = int(input("\u001b[36;1m[\u001b[0m\033[4mdropout.black\033[0m\u001b[36;1m]\u001b[0m Amount \u001b[36;1m->\u001b[0m "))
    print()

    for x in range(amount):
        threads.append(threading.Thread(target=client._create_account, args=(invite,)).start())

    for x in threads:
        try:
            x.join()
        except Exception:
            pass
