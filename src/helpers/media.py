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
from src.paths import paths

def play_sound(name):
    snd = load_sound(name)
    if snd:
        snd.play()

def load_sound(name):
    sp = os.path.join(paths.bundle_root, 'sounds', name)
    if not os.path.isfile(sp):
        sp = os.path.join(paths.sounds, name)

    if os.path.isfile(sp):
        return media.load(sp, streaming=False)
