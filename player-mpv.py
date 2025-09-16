import time
import os
import subprocess
import mpv
import mqueue

current_uuid = None
should_be_paused = False

display_video = (os.getenv("MZ_VIDEO") == "true")

if display_video:
        os.environ["DISPLAY"] = ":0.0"
        subprocess.check_call(os.path.join(os.path.dirname(os.path.abspath(__file__)), "configure-screen.sh"))
else:
    pass

player = mpv.MPV()

if display_video:
    player.fullscreen = True

queue = mqueue.Queue()
stash = mqueue.Stash()

def start_playing(uuid, ytid):
        global current_uuid, should_be_paused, player
        if current_uuid is not None:
                stop_playing()
        if player is None:
                player = mpv.MPV()
                if display_video:
                    player.fullscreen = True
        if player.filename is not None:
            player.stop = True
        if stash.exists(ytid):
            current_uuid = uuid
            player.loadfile(stash.path_for(ytid))
            should_be_paused = False

def stop_playing():
        global current_uuid, player
        assert current_uuid is not None
        current_uuid = None
        player.command('stop')

def playback_pause():
        global should_be_paused, player
        should_be_paused = not should_be_paused
        # This is stupid... but it didn't work just using =...
        # There's probably a reason for this, and I don't care at all, because this works.
        if should_be_paused:
            player.pause = True
        else:
            player.pause = False

def check_finished_uuid():
        global current_uuid, player
        if player is not None and player.filename is None:
                uuid = current_uuid
                current_uuid = None
                return uuid
        else:
                return False

def on_pause():
        global player
        if player is not None and player.filename is not None:
            playback_pause()

def on_navigate(rel: float):
        global player
        if player is not None and player.filename is not None:
                nt = player.time_pos + rel
                if nt < 0:
                        nt = 0
                player.time_pos = nt

def on_speed(mul: float):
        global player
        if player is not None and player.filename is not None:
            if 0.1 <= mul <= 10:
                player.speed = mul

queue.subscribe_on_pause(on_pause)
queue.subscribe_on_navigate(on_navigate)
queue.subscribe_on_speed(on_speed)

def status_update():
        global player
        if player is None:
                return
        queue.set_playback_status({"paused": player.pause, "time": player.time_pos or 0, "length": player.duration or 0, "speed": player.speed or 1.0})

while True:
        if player is not None and player.filename is not None and player.pause != should_be_paused:
            player.pause = True
        status_update()
        queue.check_messages()
        quent = queue.current_playable_on_queue()
        removed_uuid = check_finished_uuid()
        if removed_uuid and quent and removed_uuid == quent.uuid:
            queue.dequeue_playable()
            quent = queue.current_playable_on_queue()
        if quent:
            if quent.uuid != current_uuid:
                queue.record_play_start(quent.ytid)
                start_playing(quent.uuid, quent.ytid)
        else:
            if current_uuid is not None:
                stop_playing()

        time.sleep(0.5)
