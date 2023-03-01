import asyncio
from threading import Lock, Thread, Condition

from MasterService.Logging import *
from MasterService.AddressHelper import AddressHelper


def _get_resp_and_approves(x):
    approves_cnt = 0 
    resp_cnt = 0
    for task in x: 
        if not task.done(): 
            continue 
        else: 
            resp_cnt += 1 
        if task.result(): 
            approves_cnt += 1 
    return (resp_cnt, approves_cnt)


class MessageSheduler():
    def __init__(self):
        self.task_list = []
        self.loop = asyncio.new_event_loop()
        runner = Thread(target=self.start)
        runner.start()

    def start(self):
        self.loop.run_until_complete(self.runner())

    async def runner(self):
        while True:
            if len(self.task_list) == 0:
                await asyncio.sleep(1)
            else:
                await self.task_list.pop()

    def create_task(self, func, *args, **kwargs):
        task = self.loop.create_task(func(*args, **kwargs))
        self.task_list.append(task)
        return task


class MasterDomainMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class MasterDomain(metaclass=MasterDomainMeta):
    def __init__(self, addr_helper: AddressHelper, retry_cnt):
        self.addr_helper = addr_helper
        self.number_of_retries = retry_cnt
        self.messages_mtx = Lock()
        self.last_message_id = 0
        self.messages = []
        self.sheduler = MessageSheduler()

    # Should send message, do self.number_of_retries retries on fail, 
    # Returns true if message sent, false if all retries failed
    async def send_message(self, channel, id_and_message, notify_cond):
        await asyncio.sleep(channel)
        domain_log("Message Sent!")
        with notify_cond:
            notify_cond.notify()
        return True

    def send_message_to_secondaries(self, id_and_message):
        background_tasks = set()
        required_responces = len(self.addr_helper.GetChannels())    
        required_approves = required_responces    
        condition = Condition()

        for ch in self.addr_helper.GetChannels():
            task = self.sheduler.create_task(self.send_message, ch, id_and_message, condition)
            background_tasks.add(task)

        resp_cnt = 0
        while resp_cnt < len(background_tasks):
            # Looks like it will check nonstop after first message, but I am lazy 
            with condition:
                condition.wait(timeout=10)
                resp_cnt, approves_cnt = _get_resp_and_approves(background_tasks)
                if approves_cnt >= required_approves:
                    return True

        return False

    def add_message(self, message):
        domain_log("Adding message")
        with self.messages_mtx:
            id_msg = [self.last_message_id, message]
            self.last_message_id += 1
            self.messages.append(id_msg.copy())

        return self.send_message_to_secondaries(id_msg)

    def get_messages(self):
        domain_log("Getting messages")
        return []
