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

        self.controllers['Arm'].cmd_queue.put(-20)
    
    def key_input(self, key_queue):
        while True:
            keys = input() # 入力を受け取る
            key_queue.put(keys, True) # 受け取ったら即キューに送信

    def run(self):
        # 実際の動作をここに書く
        
        while True:
            # キーボードのキューの確認
            try:
                keys = None # 何かしら入れておく特に大きな意味はない
                
                # 0.1秒経過してもキューが空だったらmp.Empty例外が出る
                keys = self.key_queue.get(timeout = 0.1)

                if 's' in keys or 'S' in keys: #ストップ
                    self.controllers['Motor'].cmd_queue.put((0,0))
                elif 'g' in keys or 'G' in keys:
                    self.controllers['Motor'].cmd_queue.put((10000, 10000))
                elif 'r' in keys or 'R' in keys:
                    self.controllers['Motor'].cmd_queue.put((-5000, 5000))
                elif 'l' in keys or 'L' in keys:
                    self.controllers['Motor'].cmd_queue.put((5000, -5000))
                elif 'b' in keys or 'B' in keys:
                    self.controllers['Motor'].cmd_queue.put((-10000,-10000))
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
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample/yes.wav')
                elif '進め' in julius_msg:
                    self.controllers['Motor'].cmd_queue.put((10000,10000))
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample/yes.wav')
                elif '右' in julius_msg:
                    self.controllers['Motor'].cmd_queue.put((-5000, 5000))
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample/yes.wav')
                elif '左' in julius_msg:
                    self.controllers['Motor'].cmd_queue.put((5000, -5000))
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample/yes.wav')
                elif '下がれ' in julius_msg:
                    self.controllers['Motor'].cmd_queue.put((-10000,-10000))
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample/yes.wav')
                elif 'やれ' in julius_msg:
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample/test.wav')
                    self.controllers['Arm'].cmd_queue.put(50)
                    time.sleep(1)
                    self.controllers['Arm'].cmd_queue.put(-20)
                else :
                    pass
            except queue.Empty:
                pass
        
def main():
    robot = SampleRobot()
    
    robot.run()

if __name__ == '__main__':
    main()
