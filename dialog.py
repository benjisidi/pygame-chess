import wx
import os

class load_screen(wx.Frame):

	def __init__(self):
		self.wildcard = "Saved Chess Games (*.ch)|*.ch|" \
					"All files (*.*)|*.*"
		self.currentDirectory = os.getcwd()


	def pick_file(self):
		dlg = wx.FileDialog(
			None, message="Choose a file",
			defaultDir=self.currentDirectory, 
			defaultFile="",
			wildcard=self.wildcard,
			style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR
			)
	
		if dlg.ShowModal() == wx.ID_OK:
			paths = dlg.GetPaths()
			print "You chose the following file(s):"
			for path in paths:
				print path
			return paths

		dlg.Destroy()