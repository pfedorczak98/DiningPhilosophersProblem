import threading
import time
from termcolor import colored

lock = threading.Lock()
N = 5
TABLE = []
FORKS = []


# States
# 0 - Thinking
# 1 - Getting Hungry
# 2 - Eating spaghetti


class Philosopher(threading.Thread):
    def __init__(self, number):
        super().__init__(target=self.lifecycle)
        self.number = number
        self.spaghetti = 0
        self.status = '0'
        self.cnd = threading.Condition()

    def lifecycle(self):
        self.cnd.acquire()
        while True:
            self.hungry()
            # print("cp1")
            while not self.checking():
                # print("cp2")
                self.cnd.wait()
            self.eating()
            # print("cp3")
            self.thinking()

    def eating(self):
        self.status = '2'
        eating_time = 2.5
        # print("cp4")
        FORKS[self.number].pick_up(self)
        FORKS[(self.number + 1) % N].pick_up(self)
        print(f'Philosopher {self.number}', colored('started', 'green'), colored('eating', 'green'))
        time.sleep(eating_time)
        self.spaghetti += 1
        FORKS[self.number].put_back(self)
        FORKS[(self.number + 1) % N].put_back(self)
        print(f'Philosopher {self.number}', colored('finished', 'red'), colored('eating', 'red'))

        if TABLE[(self.number + 1) % N].status == "1":
            TABLE[(self.number + 1) % N].cnd.acquire()
            TABLE[(self.number + 1) % N].cnd.notify()
            TABLE[(self.number + 1) % N].cnd.release()
        if TABLE[(self.number - 1) % N].status == "1":
            TABLE[(self.number - 1) % N].cnd.acquire()
            TABLE[(self.number - 1) % N].cnd.notify()
            TABLE[(self.number - 1) % N].cnd.release()

    def thinking(self):
        self.status = '0'
        print(f'Philosopher {self.number}', colored('started', 'yellow'), colored('thinking', 'yellow'))
        lock.release()
        think_time = 2.5
        time.sleep(think_time)

    def checking(self) -> bool:
        lock.acquire()
        # waiter actions
        if self.status == '1':
            if FORKS[self.number].taken or FORKS[(self.number + 1) % N].taken:
                lock.release()
                return False

        if TABLE[(self.number - 1) % N].status == "1" and TABLE[(self.number - 1) % N].spaghetti < self.spaghetti:
            TABLE[(self.number - 1) % N].cnd.acquire()
            TABLE[(self.number - 1) % N].cnd.notify()
            TABLE[(self.number - 1) % N].cnd.release()
            lock.release()
            return False

        if TABLE[(self.number + 1) % N].status == "1" and TABLE[(self.number + 1) % N].spaghetti < self.spaghetti:
            TABLE[(self.number + 1) % N].cnd.acquire()
            TABLE[(self.number + 1) % N].cnd.notify()
            TABLE[(self.number + 1) % N].cnd.release()
            lock.release()
            return False
        return True

    def hungry(self):
        lock.acquire()
        self.status = '1'
        lock.release()


class Fork:
    def __init__(self, number):
        self.number = number
        self.taken = False

    def put_back(self, p):
        print(f'Philosopher {p.number}', colored('put', 'cyan'), colored('back', 'cyan'),f'fork {self.number}')
        self.taken = False

    def pick_up(self, p):
        print(f'Philosopher {p.number}', colored('took', 'cyan'), f'fork {self.number}\n')
        self.taken = True


def main():
    print('start')
    global N, TABLE, FORKS
    TABLE = [Philosopher(i) for i in range(N)]
    FORKS = [Fork(i) for i in range(N)]

    for i in TABLE:
        i.start()


if __name__ == '__main__':
    main()
