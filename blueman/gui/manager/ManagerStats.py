#
#
# blueman - statusbar_with_stats module
# (c) 2007 Valmantas Paliksa <walmis at balticum-tv dot lt>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

import blueman.Lib as Lib
import gobject
import gtk

from blueman.gui.Animation import Animation
from blueman.main.SpeedCalc import SpeedCalc
from blueman.Functions import get_icon, adapter_path_to_name
from blueman.Functions import format_bytes

import gettext
_ = gettext.gettext


class ManagerStats:
	
	def __init__(self, blueman):
		
		blueman.List.connect("adapter-changed", self.on_adapter_changed)
		
		if blueman.List.Adapter:
			self.hci = adapter_path_to_name(blueman.List.Adapter.GetObjectPath())
		else:
			self.hci = None
		
		self.time= None
		
		self.up_speed = SpeedCalc()
		self.down_speed = SpeedCalc()
			
		up = get_icon("blueman-up-inactive", 15)
		down = get_icon("blueman-down-inactive", 15)
		self.im_upload = gtk.Image()
		self.im_upload.set_tooltip_text(_("Data activity indication"))
		self.im_upload.set_from_pixbuf(up)
		self.im_download = gtk.Image()
		self.im_download.set_tooltip_text(_("Data activity indication"))
		self.im_download.set_from_pixbuf(down)
		self.im_upload.set_alignment(1, 0.5)
		self.im_download.set_alignment(1, 0.5)
		

		
		self.down_rate = gtk.Label()
		self.down_rate.show()
		self.down_rate.set_alignment(1, 0.5)
		self.down_rate.set_tooltip_text(_("Total data received and rate of transmission"))
		
		self.up_rate = gtk.Label()
		self.up_rate.show()
		self.up_rate.set_alignment(1, 0.5)
		self.up_rate.set_tooltip_text(_("Total data sent and rate of transmission"))
		
		self.uparrow = gtk.Image()
		self.uparrow.set_tooltip_text(_("Total data sent and rate of transmission"))
		self.uparrow.set_from_stock(gtk.STOCK_GO_UP, 1)
		self.uparrow.set_alignment(1, 0.5)
		
		self.downarrow = gtk.Image()
		self.downarrow.set_tooltip_text(_("Total data received and rate of transmission"))
		self.downarrow.set_from_stock(gtk.STOCK_GO_DOWN, 1)
		
		self.hbox = hbox = blueman.Builder.get_object("statusbar2")

		hbox.pack_start(self.uparrow, True, False)
		hbox.pack_start(self.up_rate, False, False)
		
		hbox.pack_start(self.downarrow, False, False)
		hbox.pack_start(self.down_rate, False, False)
		
		hbox.pack_start(gtk.VSeparator(), False, False)
		
		hbox.pack_start(self.im_upload, False, False)
		hbox.pack_start(self.im_download, False, False)
		hbox.show_all()
		self.on_adapter_changed(blueman.List, blueman.List.GetAdapterPath())
		
		self.up_blinker = Animation(self.im_upload, [get_icon("blueman-up-inactive", 15), get_icon("blueman-up-active", 15)])
		#self.down_blinker = Animation(self.im_download, ["/down_inactive.png", "/down_active.png"])
		self.down_blinker = Animation(self.im_download, [get_icon("blueman-down-inactive", 16), get_icon("blueman-down-active", 16)])
		
		self.start_update()
		
	def on_adapter_changed(self, List, adapter_path):
		if adapter_path != None:
			self.hci = adapter_path_to_name(adapter_path)
			self.hbox.props.sensitive = True
		else:
			self.hci = None
			self.hbox.props.sensitive = False
			
		self.up_speed.reset()
		self.down_speed.reset()
		
	def set_blinker_by_speed(self, blinker, speed):
		
		if speed > 0 and not blinker.status():
			blinker.start()
			
		if speed > (30*1024) and blinker.status():
			blinker.set_rate(20)
		elif speed > (20*1024) and blinker.status():
			blinker.set_rate(15)
		elif speed > (10*1024) and blinker.status():
			blinker.set_rate(10)
		elif speed > 1024 and blinker.status():
			blinker.set_rate(5)
		elif speed == 0 and blinker.status():

			blinker.stop()
		else:
			blinker.set_rate(1)
	
	
	def _update(self):
		#if self.hbox.parent.parent.parent.props.visible:

		if self.hci != None:
			devinfo = Lib.device_info(self.hci)
			_tx = devinfo["stat"]["byte_tx"]
			_rx = devinfo["stat"]["byte_rx"]

			tx, s_tx = format_bytes(_tx)
			rx, s_rx = format_bytes(_rx)
	
			_u_speed = self.up_speed.calc(_tx)
			_d_speed = self.down_speed.calc(_rx)
	
			self.set_blinker_by_speed(self.up_blinker, _u_speed)
			self.set_blinker_by_speed(self.down_blinker, _d_speed)
	

	
			u_speed, s_u_speed = format_bytes(_u_speed)
			d_speed, s_d_speed = format_bytes(_d_speed)
	
			self.set_data(tx, s_tx, rx, s_rx, u_speed, s_u_speed, d_speed, s_d_speed)
		
		return 1



	def start_update(self):
		self._update()
		self.timer = gobject.timeout_add (1000, self._update)
		
	def stop_update(self):
		if self.timer:
			gobject.source_remove(self.timer)
	
	def set_data(self, uploaded, u_name, downloaded, d_name, u_speed, us_name, d_speed, ds_name):
		self.down_rate.set_markup('<span size="small">%.2f %s <i>%5.2f %s/s</i></span>' % (downloaded, d_name, d_speed, ds_name))
		self.up_rate.set_markup('<span size="small">%.2f %s <i>%5.2f %s/s</i></span>' % (uploaded, u_name, u_speed, us_name))
