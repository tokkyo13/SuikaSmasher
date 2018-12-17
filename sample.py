# coding:utf-8

import time
import threading
import multiprocessing as mp
import queue
import sys
sys.path.append('..')

import mumeikaneshige as mk

class SampleRobot(mk.Mumeikaneshige):
    """
    中間発表で見せた挙動をするロボット
    """
    def __init__(self):
        # 親クラスのコンストラクタは最初に必ず明示的に呼ぶ
        super().__init__()

        # キーボード入力のスレッドの生成
        self.key_queue = mp.Queue()
        self.th_key_input = threading.Thread(target = self.key_input, 
                              args = (self.key_queue,))
        
        self.th_key_input.start() # スレッドをスタートする

        self.controllers['Arm'].cmd_queue.put(50)
    
    def key_input(self, key_queue):
        while True:
            keys = input() # 入力を受け取る
            key_queue.put(keys, True) # 受け取ったら即キューに送信

    def run(self):
        # 実際の動作をここに書く

        # 目回しループ
        print('ready to turn')
        while True:
            # キーボードのキューの確認
            try:
                keys = None # 何かしら入れておく特に大きな意味はない
                
                # 0.1秒経過してもキューが空だったらmp.Empty例外が出る
                keys = self.key_queue.get(timeout = 0.1)

                if 's' in keys or 'S' in keys: #ストップ
                    self.controllers['Motor'].cmd_queue.put((0,0))
                    break
                elif 'r' in keys or 'R' in keys:
                    self.controllers['Motor'].cmd_queue.put((-10000, 10000))
                elif 'l' in keys or 'L' in keys:
                    self.controllers['Motor'].cmd_queue.put((10000, -10000))
                else:
                    pass
            except queue.Empty:
                pass

            # Juliusから送られる文字列の確認
            try:
                julius_msg = None 
                julius_msg = self.senders['Julius'].msg_queue.get(timeout = 0.1)
                if '止まれ' in julius_msg:
                    self.controllers['Motor'].cmd_queue.put((0,0))
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample-female/yes.wav')
                    break
                elif 'まわれ' in julius_msg:
                    self.controllers['Motor'].cmd_queue.put((-10000,10000)) # 右回転
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample-female/yes.wav')
                elif '黙れ' in julius_msg:
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample-female/yes.wav')
                    sys.exit()
                else :
                    pass
            except queue.Empty:
                pass

        # スイカ割りループ
        print('ready to smash')

        right_speed = 0
        left_speed = 0
        right_bias = 2000
        left_bias = 0
        start_time = time.time()
        recovery_time = start_time + 60

        while True:
            now_time = time.time()
            remain_time = recovery_time - now_time if recovery_time - now_time > 0 else 0
            right_bias = right_bias * (remain_time / 60)

            # キーボードのキューの確認
            try:
                keys = None # 何かしら入れておく特に大きな意味はない
                
                # 0.1秒経過してもキューが空だったらmp.Empty例外が出る
                keys = self.key_queue.get(timeout = 0.1)

                if 's' in keys or 'S' in keys: #ストップ
                    right_speed = 0
                    left_speed = 0
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample-female/yes.wav')
                elif 'g' in keys or 'G' in keys:
                    right_speed = 1000
                    left_speed = 1000
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample-female/yes.wav')
                elif 'r' in keys or 'R' in keys:
                    right_speed += -2000
                    left_bias += 2000
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample-female/yes.wav')
                elif 'l' in keys or 'L' in keys:
                    right_speed += 2000
                    left_bias += -2000
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample-female/yes.wav')
                elif 'b' in keys or 'B' in keys:
                    right_speed = -10000
                    left_bias = -10000
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample-female/yes.wav')
                elif 'd' in keys or 'D' in keys:
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample-female/test.wav')
                    time.sleep(1)
                    self.controllers['Arm'].cmd_queue.put(-40)
                    time.sleep(2)
                    break
                else:
                    pass
            except queue.Empty:
                pass

            # Juliusから送られる文字列の確認
            try:
                julius_msg = None 
                julius_msg = self.senders['Julius'].msg_queue.get(timeout = 0.1)
                if '止まれ' in julius_msg:
                    right_speed = 0
                    left_speed = 0
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample-female/yes.wav')
                elif '進め' in julius_msg:
                    right_speed = 1000
                    left_speed = 1000
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample-female/yes.wav')
                elif '右' in julius_msg:
                    right_speed += -2000
                    left_bias += 2000
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample-female/yes.wav')
                elif '左' in julius_msg:
                    right_speed += 2000
                    left_bias += -2000
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample-female/yes.wav')
                elif '下がれ' in julius_msg:
                    right_speed = -10000
                    left_bias = -10000
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample-female/yes.wav')
                elif 'やれ' in julius_msg:
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample-female/test.wav')
                    time.sleep(1)
                    self.controllers['Arm'].cmd_queue.put(-40)
                    time.sleep(2)
                    break
                else :
                    pass
            except queue.Empty:
                pass

            if right_speed == 0 and left_speed == 0:
                self.controllers['Motor'].cmd_queue.put((0, 0))
            else:
                self.controllers['Motor'].cmd_queue.put((right_speed + right_bias, left_speed + left_bias))
        
        stole = self.senders['DetectStall'].msg_queue.get()
        if stole == 1:
            print('success')
            self.controllers['JTalk'].cmd_queue.put('./voice-sample-female/success.wav')
        else:
            print('fail')
            self.controllers['JTalk'].cmd_queue.put('./voice-sample-female/failure.wav')
        time.sleep(2)
        self.controllers['Arm'].cmd_queue.put(40)

def main():
    robot = SampleRobot()
    while True:
        robot.run()

if __name__ == '__main__':
    main()
