# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
import os
import sys
import subprocess

replay = sys.argv[1]
lua_path = replay + '.lua'
method = 'teamreplay'

assert os.path.exists(replay)
# assert os.path.exists(lua_path)

binary = os.path.abspath('../../build/minirts-backend')
player1 = 'dummy,fs=1'
player2 = 'dummy,fs=1'
if not os.path.exists(lua_path):
    print('lua_path %s not exist, use %s instead' % (lua_path, os.path.join(os.path.dirname(binary), '?.lua')))
    lua_path = os.path.dirname(binary)
    method = 'replay'

cmd = [
    'LUA_PATH=%s' % (os.path.join(lua_path, '?.lua')),
    binary,
    method,
    '--load_replay %s' % replay,
    '--players "%s;%s"' % (player1, player2),
    '--lua_files %s' % lua_path,
    '--max_tick %d' % 20000,
    '--vis_after %d' % 0,
]

cmd = ' '.join(cmd)
print(cmd)
subprocess.run([cmd], shell=True)
