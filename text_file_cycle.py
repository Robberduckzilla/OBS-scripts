# Author:   Robberduckzilla
# Version:  0.1b

import obspython as obs
from pathlib import Path
from datetime import datetime
import random
import sys


class TextCycler:
    def __init__(self, source_name=None):

        self.lines = [x for x in open(
            'C:/Users/Isabelle/iCloudDrive/01 Design/personal OBS graphics/OBS-scripts/input.txt',
            'r').readlines() if x != '']
        random.shuffle(self.lines)
        self.source_name = source_name
        self.line_index = 0
        self.lastCount = ''

    def update_frequency(self, frequency_in_seconds):
        self.line_change_frequency_seconds = frequency_in_seconds

    def update_text(self, force=False):
        """
        ¯\_(ツ)_/¯
        """
        source = obs.obs_get_source_by_name(self.source_name)
        if source is not None:
            if Data._timerRunning_:
                text_output = self.choose_text_line()

            # prevent more work being done than necessary
            if(text_output == self.lastCount and not force):
                return
            self.lastCount = text_output

            settings = obs.obs_data_create()
            obs.obs_data_set_string(settings, 'text', text_output)
            obs.obs_source_update(source, settings)
            obs.obs_data_release(settings)
            obs.obs_source_release(source)

    def choose_text_line(self):
        text_output = Data._format_

        self.line_index += 1
        if self.line_index >= len(self.lines):
            self.line_index = 0
        next_line = self.lines[self.line_index].strip()
        if '{text}' in Data._format_:
            text_output = str.replace(text_output, '{text}', f'{next_line}')
        return text_output


class Data:
    _defaultFormat_ = '{text}'
    _format_ = _defaultFormat_
    _autoStart_ = True
    _timerRunning_ = True
    _timeBetweenMessages_ = 1


text_cycler = TextCycler()
callback = text_cycler.update_text


def start_timer():
    obs.timer_remove(callback)
    obs.timer_add(callback, Data._timeBetweenMessages_ * 1000)
    Data._timerRunning_ = True


def stop_timer():
    Data._timerRunning_ = False

def start_pressed(props, prop):
    start_timer()


def script_update(settings):
    text_cycler.source_name = obs.obs_data_get_string(settings, 'source')
    Data._format_ = obs.obs_data_get_string(settings, 'format')
    Data._timeBetweenMessages_ = obs.obs_data_get_int(
        settings, 'seconds_between_lines')

    # force the text to update and do not increment the timer
    # text_cycler.update_text(True)


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

    obs.obs_properties_add_text(
        props, 'format', 'Text Format:', obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_int_slider(
        props, 'seconds_between_lines', 'Seconds Between:', 1, 60, 1)
    obs.obs_properties_add_button(
        props, 'start_button', 'Start Cycling', start_pressed)

    return props


def script_load(settings):
    Data._format_ = obs.obs_data_get_string(settings, 'format')
    Data._timeBetweenMessages_ = obs.obs_data_get_int(
        settings, 'seconds_between_lines')
    if not Data._format_:
        Data._format_ = Data._defaultFormat_

    obs.obs_data_set_string(settings, 'format', Data._format_)
    obs.obs_data_set_int(settings, 'seconds_between_lines',
                         Data._timeBetweenMessages_)
