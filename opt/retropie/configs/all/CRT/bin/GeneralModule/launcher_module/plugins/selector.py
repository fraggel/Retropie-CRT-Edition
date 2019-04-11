#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
launcher selector.py.

launcher library for retropie, based on original idea - Ironic
  and the retropie integration work by -krahs-

https://github.com/krahsdevil/crt-for-retropie/

Copyright (C)  2018/2019 -krahs- - https://github.com/krahsdevil/
Copyright (C)  2019 dskywalk - http://david.dantoine.org

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 2 of the License, or (at your option) any
later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import os, sys
from launcher_module.core import CFG_VIDEOUTILITY_FILE
from launcher_module.plugins.libretro import libretro, logging, RETROARCH_CONFIGS_PATH, AUTOFREQ_DATABASE
from launcher_module.file_helpers import ini_get, add_line, remove_line
from launcher_module.utils import compact_rom_name


LABELS50HZ = ["pal","nl","e","s","sw","fn","g","uk","gr","i","h","eu",
                "europe","europa","spain","germany","france","italy"]
LABELS60HZ = ["ntsc","1","4","a","j","b","k","c","u","hk","world","usa",
                "us","ue","jue","jap","jp","japan","japon","asia","usa,europe",
                "europe,usa","japan,usa","usa,japan"]
ALLOWED_FREQS = ["50", "60"]

class selector(libretro):
    m_sCompactedName = ""
    m_sFrequency = ""
    m_sSelectFreq = ""
    # FIXME: aun no se muy bien como haré esto... (pues imagina yo)
    @staticmethod
    def get_system_list():
        return ["megadrive", "segacd", "sega32x", "mastersystem", "n64", "nes", "snes",
                "psx", "msx", "atari2600", "odyssey2", "zx81", "atarist", "c64", "atari7800"]

    def system_setup(self):
        super(selector, self).system_setup()
        self.m_sSelectFreq = ini_get(CFG_VIDEOUTILITY_FILE, "freq_selector")

        # first i try to find an allowed freq
        if self.m_sSelectFreq in ALLOWED_FREQS:
            logging.info("Frequency selector always %sHz" % self.m_sSelectFreq)
        elif self.m_sSelectFreq == "100":
            logging.info("Frequency selector mode auto")
            self.m_sSelectFreq = self.frecuency_auto()
        else:
            logging.info("Frequency selector mode manual")
            self.m_sSelectFreq = self.frequency_manual()

        self.m_sSystemCfg = self.m_sSystemFreq
        if self.m_sSelectFreq == "50":
            self.m_sSystemCfg += "50"

        self.m_sSystemCfg += ".cfg"
        self.m_sSystemCfgPath = os.path.join(RETROARCH_CONFIGS_PATH, self.m_sSystemCfg)
        logging.info("enabled selector cfg: %s" % self.m_sSystemCfgPath)

    def frecuency_auto(self):
        self.m_sCompactedName = compact_rom_name(self.m_sRomFile)
        self.check_frequency_database()
        sFrequency = self.find_rom_frequency_database()
        if not sFrequency:
            sFrequency = self.find_frequency_in_name()
            if not sFrequency:
                sFrequency = self.frequency_manual()
        return sFrequency

    def frequency_manual(self):
        return "60"

    def check_frequency_database(self):
        if not os.path.isfile(AUTOFREQ_DATABASE):
            os.mkdir(AUTOFREQ_DATABASE)
            logging.info("Created frequency database")

    def find_rom_frequency_database(self):
        sFreqValue = ini_get(AUTOFREQ_DATABASE, self.m_sCompactedName)
        if sFreqValue in ALLOWED_FREQS:
            logging.info("Game found in current frequency database at %sHz" % sFreqValue)
            return sFreqValue
        elif not sFreqValue:
            logging.info("Game not found in current frequency database")
            return ""
        else:
            logging.info("Game found in current database with wrong Frequency")
            self.clean_loadedgame_frequency_database()
            return ""

    def clean_loadedgame_frequency_database(self):
        if remove_line(AUTOFREQ_DATABASE, self.m_sCompactedName):
            logging.info("Game was cleaned")
        else:
            logging.error("Game could not be cleaned")

    def find_frequency_in_name(self):
        for CountryCODE in LABELS60HZ:
            if "(%s)"%CountryCODE in self.m_sRomFile.lower() or "[%s]"%CountryCODE in self.m_sRomFile.lower():
                add_line(AUTOFREQ_DATABASE, "%s 60" % self.m_sCompactedName)
                logging.info("60Hz Frequency label identified for: %s" % self.m_sRomFile)
                return "60"
        for CountryCODE in LABELS50HZ:
            if "(%s)"%CountryCODE in self.m_sRomFile.lower() or "[%s]"%CountryCODE in self.m_sRomFile.lower():
                add_line(AUTOFREQ_DATABASE, "%s 50" % self.m_sCompactedName)
                logging.info("60Hz Frequency label identified for: %s" % self.m_sRomFile)
                return "50"
        return ""
