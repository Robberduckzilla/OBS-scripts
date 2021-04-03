
import obspython as obs
from pathlib import Path
from datetime import datetime
import random
import sys


class BreakTimer:
    def __init__(self, source_name=None, timer_duration=None):
        self.source_name = source_name
        self.lastCount = ''
        self.timer_duration_seconds = 5 * 60
 

    def update_clock_length(self, timer_duration_minutes):
        self.timer_duration_seconds = timer_duration_minutes * 60


    def update_text(self, force=False):
        source = obs.obs_get_source_by_name(self.source_name)
        if source is not None:


            
            if Data._timerRunning_:
                if self.timer_duration_seconds > 0:
                    minutes, seconds = divmod(self.timer_duration_seconds, 60)
                else:
                    minutes = 0
                    seconds = 0

            text_output = f'{minutes:02}:{seconds:02}'

            # prevent more work being done than necessary
            if(text_output == self.lastCount and not force):
                return
            self.lastCount = text_output
            self.timer_duration_seconds -= 1
            settings = obs.obs_data_create()
            obs.obs_data_set_string(settings, 'text', text_output)
            obs.obs_source_update(source, settings)
            obs.obs_data_release(settings)
            obs.obs_source_release(source)


class Data:
    _defaultFormat_ = '{text}'
    _format_ = _defaultFormat_
    _autoStart_ = True
    _timerRunning_ = True
    _timerDuration_ = 1


break_timer = BreakTimer()
callback = break_timer.update_text


def start_timer():
    break_timer.update_clock_length(Data._timerDuration_)
    obs.timer_remove(callback)
    obs.timer_add(callback, 1 * 1000)
    Data._timerRunning_ = True


def stop_timer():
    Data._timerRunning_ = False


def start_pressed(props, prop):
    start_timer()


def script_update(settings):
    break_timer.source_name = obs.obs_data_get_string(settings, 'source')
    Data._format_ = obs.obs_data_get_string(settings, 'format')
    Data._timerDuration_ = obs.obs_data_get_int(
        settings, 'timer_duration')


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

    obs.obs_properties_add_int_slider(
        props, 'timer_duration', 'Timer Duration (Mins):', 1, 120, 1)
    obs.obs_properties_add_button(
        props, 'start_button', 'Start Countdown', start_pressed)

    return props


def script_load(settings):
    Data._format_ = obs.obs_data_get_string(settings, 'format')
    Data._timerDuration_ = obs.obs_data_get_int(
        settings, 'timer_duration')
    if not Data._format_:
        Data._format_ = Data._defaultFormat_

    obs.obs_data_set_string(settings, 'format', Data._format_)
    obs.obs_data_set_int(settings, 'timer_duration',
                         Data._timerDuration_)
