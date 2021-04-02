# Author:   Robberduckzilla
# Version:  0.1

import obspython as obs
from pathlib import Path
from datetime import datetime
import random

class CountdownToStream:
    def __init__(self,source_name=None):
        self.source_name = source_name
        self.lines = random.shuffle([x for x in open('C:/Users/robmd/Actual Local Files/GitHub/OBS-scripts/input.txt', 'r').readlines() if x !=''])
        self.line_index = 0
        self.line_change_frequency_seconds = 1
        self.lastCount = ''

    def update_text(self, force=False, updateTime=True):
        source = obs.obs_get_source_by_name(self.source_name)
        if source is not None:
            if not Data._timerRunning_:
                text_output = ''
            else:
                text_output = self.get_formatted_time()

            #prevent more work being done than necessary
            if(text_output == self.lastCount and not force):
                return

            self.lastCount = text_output
            settings = obs.obs_data_create()
            obs.obs_data_set_string(settings, 'text', text_output)
            obs.obs_source_update(source, settings)
            obs.obs_data_release(settings)
            obs.obs_source_release(source)

    def get_formatted_time(self):
        text_output = Data._format_
        
        # calculate total seconds until the date
        time_until_stream = int((datetime(2021, 4, 10, 12, 0, 0) - datetime.now()).total_seconds())
        # prevent negative seconds
        if time_until_stream <= 0:
            time_until_stream = 0
       
        if time_until_stream % self.line_change_frequency_seconds == 0:            
            self.line_index +=1
            if self.line_index >= len(self.lines):
                self.line_index = 0

        next_line = self.lines[self.line_index]

        if '{text}' in Data._format_:
            text_output = str.replace(text_output, '{text}', f'{next_line}')

        return text_output

class Data:
    _defaultFormat_ = '{text}'
    _format_ = _defaultFormat_
    _autoStart_ = True
    _timerRunning_ = True

stream_countdown = CountdownToStream()
callback = stream_countdown.update_text

# ---------------------------- helper methods --------------------------------------

def start_timer():
    Data._timerRunning_ = True
    obs.timer_add(callback, 1 * 1000)

# --------------------------- callbacks ---------------------------------------------

def start_pressed(props, prop):
    start_timer()

def on_event(event):
    #if both autostart and autostop are diabled just return
    if not Data._autoStart_: return

    #stream start
    if event == obs.OBS_FRONTEND_EVENT_STREAMING_STARTED and Data._autoStart_:
        if stream_countdown.source_name != '':
            start_timer()

# -------------------------------------- script methods ----------------------------------------

def script_update(settings):
    stream_countdown.source_name = obs.obs_data_get_string(settings, 'source')
    Data._format_ = obs.obs_data_get_string(settings, 'format')
    Data._autoStart_ = obs.obs_data_get_bool(settings, 'auto_start')

    #force the text to update and do not increment the timer
    stream_countdown.update_text(True, False)

def script_properties():
    props = obs.obs_properties_create()
    p = obs.obs_properties_add_list(
        props,
        'source',
        'Text Source:',
        obs.OBS_COMBO_TYPE_EDITABLE,
        obs.OBS_COMBO_FORMAT_STRING,
    )

    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = obs.obs_source_get_unversioned_id(source)
            if source_id == 'text_gdiplus' or source_id == 'text_ft2_source':
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(p, name, name)

        obs.source_list_release(sources)

    obs.obs_properties_add_text(props, 'format', 'Text Format:', obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_button(props, 'start_button', 'Start Timer', start_pressed)
    obs.obs_properties_add_bool(props, 'auto_start', 'Start Automatically with Stream')

    return props

def script_load(settings):
    obs.obs_frontend_add_event_callback(on_event)
    Data._format_ = obs.obs_data_get_string(settings, 'format')
    Data._autoStart_ = obs.obs_data_get_bool(settings, 'auto_start')

    if not Data._format_:
        Data._format_ = Data._defaultFormat_

    obs.obs_data_set_string(settings, 'format', Data._format_)
    obs.obs_data_set_bool(settings, 'auto_start', Data._autoStart_)
