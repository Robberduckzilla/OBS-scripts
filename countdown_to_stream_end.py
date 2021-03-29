#
# Author:   Robberduckzilla
# Version:  0.1
import obspython as obs
from pathlib import Path
from datetime import datetime

class CountdownToSleep:
    def __init__(self,source_name=None):
        self.source_name = source_name
        self.lastCount = ""
        self.seconds_till_sleep = 0

    def update_text(self, force=False, updateTime=True):
        source = obs.obs_get_source_by_name(self.source_name)
        if source is not None:
            if(Data._visible_ and not Data._timerRunning_):
                countdown = ""
            else:
                countdown = self.get_formatted_time()

            #prevent more work being done than necessary
            if(countdown == self.lastCount and not force):
                return

            self.lastCount = countdown
            settings = obs.obs_data_create()
            obs.obs_data_set_string(settings, "text", countdown)
            obs.obs_source_update(source, settings)
            obs.obs_data_release(settings)
            obs.obs_source_release(source)

    def get_formatted_time(self):
        countdown = Data._format_
        
        time_until_sleep = int((datetime(2021, 4, 11, 12, 0, 0) - datetime.now()).total_seconds())
        if time_until_sleep <= 0:
            time_until_sleep = 0
        
        hours, remainder = divmod(time_until_sleep, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        hours = f"{int(hours):02}"
        minutes = f"{int(minutes):02}"
        seconds = f"{int(seconds):02}"
         
       
        if "{time}" in Data._format_:
            countdown = str.replace(countdown, "{time}", f'{hours}:{minutes}:{seconds}')

        return countdown

class Data:
    _defaultFormat_ = "{s} seconds remain."
    _format_ = _defaultFormat_
    _autoStart_ = False
    _autoStop_ = False
    _recording_ = False
    _visible_ = False
    _timerRunning_ = False

liveTime = CountdownToSleep()
callback = liveTime.update_text

# ---------------------------- helper methods --------------------------------------

def start_timer():
    Data._timerRunning_ = True
    obs.timer_add(callback, 1 * 1000)

# --------------------------- callbacks ---------------------------------------------

def start_pressed(props, prop):
    start_timer()

def on_event(event):
    #if both autostart and autostop are diabled just return
    if not Data._autoStart_ and not Data._autoStop_: return

    #stream start
    if event == obs.OBS_FRONTEND_EVENT_STREAMING_STARTED and Data._autoStart_:
        if liveTime.source_name != "":
            start_timer()

# -------------------------------------- script methods ----------------------------------------

def script_update(settings):
    liveTime.source_name = obs.obs_data_get_string(settings, "source")
    Data._format_ = obs.obs_data_get_string(settings, "format")
    Data._autoStart_ = obs.obs_data_get_bool(settings, "auto_start")

    #force the text to update and do not increment the timer
    liveTime.update_text(True, False)

def script_properties():
    props = obs.obs_properties_create()
    p = obs.obs_properties_add_list(
        props,
        "source",
        "Text Source:",
        obs.OBS_COMBO_TYPE_EDITABLE,
        obs.OBS_COMBO_FORMAT_STRING,
    )

    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = obs.obs_source_get_unversioned_id(source)
            if source_id == "text_gdiplus" or source_id == "text_ft2_source":
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(p, name, name)

        obs.source_list_release(sources)

    obs.obs_properties_add_text(props, "format", "Text Format:", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_button(props, "start_button", "Start Timer", start_pressed)
    obs.obs_properties_add_bool(props, "auto_start", "Start Automatically with Stream/Recording")

    return props

def script_load(settings):
    obs.obs_frontend_add_event_callback(on_event)
    Data._format_ = obs.obs_data_get_string(settings, "format")
    Data._autoStart_ = obs.obs_data_get_bool(settings, "auto_start")

    if not Data._format_:
        Data._format_ = Data._defaultFormat_

    obs.obs_data_set_string(settings, "format", Data._format_)
    obs.obs_data_set_bool(settings, "auto_start", Data._autoStart_)
