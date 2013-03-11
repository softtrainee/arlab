#===============================================================================
# Copyright 2011 Jake Ross
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================
import os
from pyglet import media
import time

from src.paths import paths
from threading import Event, Thread

def loop_sound(name):
    evt = Event()
    def loop():
        from pyglet import app
        snd = load_sound(name)
        player = media.Player()
        player.queue(snd)
        player.eos_action = player.EOS_LOOP
        player.play()

        app.run()
        while not evt.is_set():
            time.sleep(0.1)
        player.stop()
        app.exit()

    t = Thread(target=loop)
    t.start()
    return evt

def play_sound(name):
    snd = load_sound(name)
    if snd:
        snd.play()
        del(snd)

def load_sound(name):
    if not name.endswith('.wav'):
        name = '{}.wav'.format(name)

    sp = os.path.join(paths.bundle_root, 'sounds', name)
    if not os.path.isfile(sp):
        sp = os.path.join(paths.sounds, name)

    if os.path.isfile(sp):
        return media.load(sp, streaming=False)

#DEFAULT_SOUNDS = ['shutter']
#for di in DEFAULT_SOUNDS:
#    # load sound now so quickly available
#    load_sound('{}.wav'.format(di))
