VERSION="1.23"
PACKAGE="blueman"
PREFIX="/usr/local"
BIN_DIR="/usr/local/bin"
ICON_PATH = "/usr/local/share/blueman/icons"
UI_PATH = "/usr/local/share/blueman/ui"
OBEX_BROWSE_AVAILABLE = True
DHCP_CONFIG_FILE = "/etc/dhcp3/dhcpd.conf"
POLKIT = "yes" == "yes"
HAL_ENABLED = "no" == "yes"

DEF_BROWSE_COMMAND = "nautilus --browser obex://[%d]"

import os
import gettext
import __builtin__

translation = gettext.translation("blueman", "/usr/local/share/locale", fallback=True)
translation.install(unicode=True)
__builtin__.ngettext = translation.ungettext

if os.path.exists("../apps") and os.path.exists("../data"):
	BIN_DIR = "./"
	ICON_PATH = "../data/icons"
	UI_PATH = "../data/ui"
