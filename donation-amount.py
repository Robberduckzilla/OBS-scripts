import warnings
from datetime import datetime

import obspython as obs
import requests
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore")


class DonationAmount:
    def __init__(self, source_name=None):
        self.source_name = source_name
        self.url = "https://justgiving.com/page/heroeswantedadventures"
        self.class_name = "cp-heading-large branded-text"
        self.lastAmount = ""

    def update_text(self, force=False):
        source = obs.obs_get_source_by_name(self.source_name)
        if source is not None:

            if Data._timerRunning_:
                page = requests.get(self.url)
                soup = BeautifulSoup(page.content)
                amount = soup.find_all("div", {"class": f"{self.class_name}"})[
                    0
                ].contents
                text_output = str(amount[0])
            # prevent more work being done than necessary
            if text_output == self.lastAmount and not force:
                return
            self.lastAmount = text_output

            settings = obs.obs_data_create()
            obs.obs_data_set_string(settings, "text", text_output)
            obs.obs_source_update(source, settings)
            obs.obs_data_release(settings)
            obs.obs_source_release(source)


class Data:
    _autoStart_ = True
    _timerRunning_ = True
    _timerDuration_ = 1


donation_tracker = DonationAmount()
callback = donation_tracker.update_text


def start_timer():
    obs.timer_remove(callback)
    obs.timer_add(callback, 1 * 5000)
    Data._timerRunning_ = True


def stop_timer():
    Data._timerRunning_ = False


def start_pressed(props, prop):
    start_timer()


def script_update(settings):
    donation_tracker.source_name = obs.obs_data_get_string(settings, "source")


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

    start_timer()
    return props


def script_load(settings):
    pass
