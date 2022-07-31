import os
import sys
import random
import secrets
import aiohttp
import logging
import asyncio
import tasksio

logging.basicConfig(
    level=logging.INFO,
    format="\x1b[38;5;9m[\x1b[0m%(asctime)s\x1b[38;5;9m]\x1b[0m %(message)s\x1b[0m",
    datefmt="%H:%M:%S"
)

class Capmonster(object):

    def __init__(self, client_key: str):
        self.client_key = client_key
        self.headers = {
            "content-type": "application/json"
        }

    async def create_task(self):
        try:
            async with aiohttp.ClientSession(headers=self.headers) as client:
                json = {
                    "clientKey": self.client_key,
                    "task": {
                        "type": "HCaptchaTaskProxyless",
                        "websiteURL": "https://discord.com/",
                        "websiteKey": "f5561ba9-8f1e-40ca-9b5b-a0b3f719ef34",
                        "minScore": 0.3
                    }
                }
                async with client.post("https://api.capmonster.cloud/createTask", json=json) as response:
                    json = await response.json(content_type=None)
                    if json["errorId"] == 0:
                        return json["taskId"]
                    else:
                        return await self.create_task()
        except Exception:
            return await self.create_task()

    async def get_result(self, task_id: str):
        try:
            async with aiohttp.ClientSession(headers=self.headers) as client:
                json = {
                    "clientKey": self.client_key,
                    "taskId": task_id
                }
                async with client.get("https://api.capmonster.cloud/getTaskResult", json=json) as response:
                    json = await response.json(content_type=None)
                    if json["errorId"] == 0:
                        if json["status"] == "ready":
                            return json["solution"]["gRecaptchaResponse"]
                        else:
                            return await self.get_result(task_id)
                    else:
                        return await self.get_result(task_id)
        except Exception:
            return await self.get_result(task_id)

    async def start(self):
        task = await self.create_task()
        return await self.get_result(task)

class Discord(object):

    def __init__(self):
        if sys.platform == "linux":
            self.clear = lambda: os.system("clear")
        else:
            self.clear = lambda: os.system("cls")
       
        self.clear()

        self.tokens = []
        self.timeout = aiohttp.ClientTimeout(3)

        with open("data/proxies.txt", encoding="utf-8") as f:
            self.proxies = [i.strip() for i in f]

        self.client_key = input("\x1b[38;5;9m[\x1b[0m?\x1b[38;5;9m]\x1b[0m Capmonster apikey \x1b[38;5;9m->\x1b[0m ")
        self.mode = input("\x1b[38;5;9m[\x1b[0m?\x1b[38;5;9m]\x1b[0m Proxyless/Proxy \x1b[38;5;9m->\x1b[0m ")
        self.name_prefix = input("\x1b[38;5;9m[\x1b[0m?\x1b[38;5;9m]\x1b[0m Username prefix \x1b[38;5;9m->\x1b[0m ")
        self.invite = input("\x1b[38;5;9m[\x1b[0m?\x1b[38;5;9m]\x1b[0m Invite \x1b[38;5;9m->\x1b[0m discord.gg/")

        if self.mode.lower() == "proxyless":
            self.use_proxies = False
        else:
            self.use_proxies = True
            self.proxy_type = input("\x1b[38;5;9m[\x1b[0m?\x1b[38;5;9m]\x1b[0m Proxy type \x1b[38;5;9m->\x1b[0m ")

        self.tasks = int(input("\x1b[38;5;9m[\x1b[0m?\x1b[38;5;9m]\x1b[0m Tasks \x1b[38;5;9m->\x1b[0m "))
            
        self.capmonster_client = Capmonster(client_key=self.client_key)

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

        print()

    async def create(self, captcha: str = None):
        if not captcha: captcha = await self.capmonster_client.start()
        payload = {
            "username": "%s | %s" % (self.name_prefix, secrets.token_hex(5)),
            "email": "%s@gmail.com" % (secrets.token_hex(5)),
            "password": secrets.token_hex(10),
            "invite": self.invite,
            "consent": True,
            "captcha_key": captcha
        }
        if self.use_proxies:
            proxy = "%s://%s" % (self.proxy_type, random.choice(self.proxies))
        else:
            proxy = None
        try:
            async with aiohttp.ClientSession(headers=self.headers, timeout=self.timeout) as client:
                async with client.post("https://discord.com/api/v9/auth/register", json=payload, proxy=proxy) as response:
                    json = await response.json(content_type=None)
                    if response.status == 201:
                        logging.info(json)
                        token = json["token"]
                        logging.info("Successfully created \x1b[38;5;9m(\x1b[0m%s\x1b[38;5;9m)\x1b[0m" % (token))
                        with open("data/tokens.txt", "a+") as f:
                            f.write("%s\n" % (token))
                    else:
                        if "message" in await response.text():
                            logging.info("%s \x1b[38;5;9m(\x1b[0m%s\x1b[38;5;9m)\x1b[0m" % (json["message"], response.status))
                        else:
                            logging.info("Failed to create account \x1b[38;5;9m(\x1b[0m%s\x1b[38;5;9m)\x1b[0m" % (response.status))
        except Exception:
            logging.info("Connection error \x1b[38;5;9m(\x1b[0m000\x1b[38;5;9m)\x1b[0m")
            await self.create(captcha)

    async def start(self):
        async with tasksio.TaskPool(self.tasks) as pool:
           while True:
                await pool.put(self.create())

if __name__ == "__main__":
    client = Discord()
    asyncio.run(client.start())
