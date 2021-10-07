import pickle
from time import time

import wx
import wx.xrc

from data_checker import get_event_name_and_date


class SettingsDialog(wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition,
                           size=wx.Size(308, 246), style=wx.DEFAULT_DIALOG_STYLE)

        with open('settings.pickle', 'rb') as f:
            self.saved_settings = pickle.load(f)
            self.proxy = self.saved_settings['Proxy']
            print(self.proxy)


        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer1 = wx.BoxSizer(wx.VERTICAL)
 
        bSizer2 = wx.BoxSizer(wx.VERTICAL)

        bSizer11 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_proxies_button = wx.Button(self, wx.ID_ANY, u"Select Proxies", wx.DefaultPosition, wx.Size(150, -1), 0)
        self.m_proxies_button.Bind(wx.EVT_BUTTON, self.select_proxies)
        bSizer11.Add(self.m_proxies_button, 0, wx.ALL, 5)

        proxies_label_text = self.proxy
        print(proxies_label_text)
        self.m_proxies_label = wx.StaticText(self, wx.ID_ANY, proxies_label_text, wx.DefaultPosition,
                                             wx.DefaultSize, 0)
        self.m_proxies_label.Wrap(-1)
        bSizer11.Add(self.m_proxies_label, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        bSizer2.Add(bSizer11, 1, wx.EXPAND, 5)

        bSizer1.Add(bSizer2, 1, wx.EXPAND, 5)

        bSizer10 = wx.BoxSizer(wx.VERTICAL)

        bSizer4 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText2 = wx.StaticText(self, wx.ID_ANY, u"Gmail Email:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText2.Wrap(-1)
        bSizer4.Add(self.m_staticText2, 0, wx.ALL, 5)

        self.m_gmail_email_input = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(300, -1), 0)
        bSizer4.Add(self.m_gmail_email_input, 0, wx.ALL, 5)

        bSizer10.Add(bSizer4, 1, wx.EXPAND, 5)

        bSizer41 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText21 = wx.StaticText(self, wx.ID_ANY, u"Gmail Pass:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText21.Wrap(-1)
        bSizer41.Add(self.m_staticText21, 0, wx.ALL, 5)

        self.m_gmail_pass_input = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(300, -1),
                                              wx.TE_PASSWORD)
        bSizer41.Add(self.m_gmail_pass_input, 0, wx.ALL, 5)

        bSizer10.Add(bSizer41, 1, wx.EXPAND, 5)

        bSizer42 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText22 = wx.StaticText(self, wx.ID_ANY, u"Notify Email:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText22.Wrap(-1)
        bSizer42.Add(self.m_staticText22, 0, wx.ALL, 5)

        self.m_notify_email_input = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(300, -1),
                                                0)
        bSizer42.Add(self.m_notify_email_input, 0, wx.ALL, 5)

        bSizer10.Add(bSizer42, 1, wx.EXPAND, 5)

        bSizer3 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText1 = wx.StaticText(self, wx.ID_ANY, u"Master list url:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText1.Wrap(-1)
        bSizer3.Add(self.m_staticText1, 0, wx.ALL, 5)

        self.m_master_list_input = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(300, -1), 0)
        bSizer3.Add(self.m_master_list_input, 0, wx.ALL, 5)

        bSizer10.Add(bSizer3, 1, wx.EXPAND, 5)

        bSizer1.Add(bSizer10, 1, wx.EXPAND, 5)

        bSizer12 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_save_button = wx.Button(self, wx.ID_OK, u"Save Settings", wx.DefaultPosition, wx.Size(130, -1), 0)
        bSizer12.Add(self.m_save_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.m_cancel_button = wx.Button(self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.Size(154, -1), 0)
        bSizer12.Add(self.m_cancel_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        bSizer1.Add(bSizer12, 1, wx.EXPAND, 5)

        self.SetSizer(bSizer1)
        self.Layout()

        self.Centre(wx.BOTH)
        self.load_settings()

    def select_proxies(self, event):
        openFileDialog = wx.FileDialog(self, "Open", "", "",
                                       "Text files (*.txt)|*.txt",
                                       wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.ShowModal()
        self.proxy = openFileDialog.GetPath()
        self.m_proxies_label.SetLabel(self.proxy)

        openFileDialog.Destroy()

    def load_settings(self):
        self.m_gmail_email_input.SetValue(self.saved_settings['GmailEmail'])
        self.m_gmail_pass_input.SetValue(self.saved_settings['GmailPass'])
        self.m_notify_email_input.SetValue(self.saved_settings['NotifyEmail'])
        self.m_master_list_input.SetValue(self.saved_settings['MasterURL'])
        proxies_label_text = self.saved_settings['Proxy']
        print(proxies_label_text)
        self.m_proxies_label.SetLabel(proxies_label_text)

    def get_data(self):
        return {
            "GmailEmail": self.m_gmail_email_input.GetValue(),
            'GmailPass': self.m_gmail_pass_input.GetValue(),
            'NotifyEmail': self.m_notify_email_input.GetValue(),
            'MasterURL': self.m_master_list_input.GetValue(),
            'Proxy': self.proxy
        }

    def __del__(self):
        pass

class AddEventDialog(wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Add Event", pos=wx.DefaultPosition,
                           size=wx.Size(250, 370), style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        bSizer5 = wx.BoxSizer(wx.VERTICAL)

        bSizer2 = wx.BoxSizer(wx.VERTICAL)


        fgSizer1 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer1.SetFlexibleDirection(wx.BOTH)
        fgSizer1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText4 = wx.StaticText(self, wx.ID_ANY, u"URL:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText4.Wrap(-1)
        fgSizer1.Add(self.m_staticText4, 0, wx.ALL, 5)

        self.m_url = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(200, -1), 0)
        fgSizer1.Add(self.m_url, 0, wx.ALL | wx.EXPAND, 5)

        bSizer2.Add(fgSizer1, 1, wx.EXPAND, 5)
        #
        # fgSizer2 = wx.FlexGridSizer(0, 2, 0, 0)
        # fgSizer2.SetFlexibleDirection(wx.BOTH)
        # fgSizer2.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        # self.m_staticText5 = wx.StaticText(self, wx.ID_ANY, u"Date in YYYY-MM-DD", wx.DefaultPosition, wx.DefaultSize,
        #                                    0)
        # self.m_staticText5.Wrap(-1)
        # fgSizer2.Add(self.m_staticText5, 0, wx.ALL, 5)
        #
        # self.m_textCtrl5 = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(200, -1), 0)
        # fgSizer2.Add(self.m_textCtrl5, 0, wx.ALL | wx.EXPAND, 5)
        #
        # bSizer2.Add(fgSizer2, 1, wx.EXPAND, 5)
        #
        # fgSizer3 = wx.FlexGridSizer(0, 2, 0, 0)
        # fgSizer3.SetFlexibleDirection(wx.BOTH)
        # fgSizer3.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
        #
        # self.m_staticText6 = wx.StaticText(self, wx.ID_ANY, u"Event Name", wx.DefaultPosition, wx.DefaultSize, 0)
        # self.m_staticText6.Wrap(-1)
        # fgSizer3.Add(self.m_staticText6, 0, wx.ALL, 5)
        #
        # self.m_textCtrl6 = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(200, -1), 0)
        # fgSizer3.Add(self.m_textCtrl6, 0, wx.ALL | wx.EXPAND, 5)
        #
        # bSizer2.Add(fgSizer3, 1, wx.EXPAND, 5)
        #
        fgSizer4 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer4.SetFlexibleDirection(wx.BOTH)
        fgSizer4.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText7 = wx.StaticText(self, wx.ID_ANY, u"Interval (seconds)", wx.DefaultPosition, wx.DefaultSize,
                                           0)
        self.m_staticText7.Wrap(-1)
        fgSizer4.Add(self.m_staticText7, 0, wx.ALL, 5)

        self.m_textCtrl7 = wx.TextCtrl(self, wx.ID_ANY, u'259200', wx.DefaultPosition, wx.Size(120, -1), 0)
        fgSizer4.Add(self.m_textCtrl7, 0, wx.ALL, 5)

        bSizer2.Add(fgSizer4, 1, wx.EXPAND, 5)

        fgSizer4a = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer4a.SetFlexibleDirection(wx.BOTH)
        fgSizer4a.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)


        self.m_add_sec_button = wx.Button(self, wx.ID_ANY, u"Add Seconds", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_add_sec_button.Bind(wx.EVT_BUTTON, self.add_seconds)
        fgSizer4a.Add(self.m_add_sec_button, 0, wx.ALL, 5)


        m_comboBox1Choices = [u"1 hour", u"12 hours", u"1 day", u"2 days", u"3 days", u"4 days", u"5 days", u"7 days",
                              u"14 days", u"30 days"]
        self.m_comboBox1 = wx.ComboBox(self, wx.ID_ANY, u"Select...", wx.DefaultPosition, wx.DefaultSize,
                                       m_comboBox1Choices, 0)
        fgSizer4a.Add(self.m_comboBox1, 0, wx.ALL, 5)

        bSizer2.Add(fgSizer4a, 1, wx.EXPAND, 5)





        fgSizer5 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer5.SetFlexibleDirection(wx.BOTH)
        fgSizer5.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText8 = wx.StaticText(self, wx.ID_ANY, u"Notification Number", wx.DefaultPosition, wx.DefaultSize,
                                           0)
        self.m_staticText8.Wrap(-1)
        fgSizer5.Add(self.m_staticText8, 0, wx.ALL, 5)

        self.m_textCtrl8 = wx.TextCtrl(self, wx.ID_ANY, u'5000', wx.DefaultPosition, wx.Size(120, -1), 0)
        fgSizer5.Add(self.m_textCtrl8, 0, wx.ALL, 5)

        bSizer2.Add(fgSizer5, 1, wx.EXPAND, 5)

        fgSizer6 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer6.SetFlexibleDirection(wx.BOTH)
        fgSizer6.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText9 = wx.StaticText(self, wx.ID_ANY, u"Ticket Row", wx.DefaultPosition, wx.DefaultSize,
                                           0)
        self.m_staticText9.Wrap(-1)
        fgSizer6.Add(self.m_staticText9, 0, wx.ALL, 5)

        self.m_textCtrl9 = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(120, -1), 0)
        fgSizer6.Add(self.m_textCtrl9, 0, wx.ALL, 5)

        bSizer2.Add(fgSizer6, 1, wx.EXPAND, 5)

        fgSizer_pass = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer_pass.SetFlexibleDirection(wx.BOTH)
        fgSizer_pass.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText_pass = wx.StaticText(self, wx.ID_ANY, u"Pre-sale pass", wx.DefaultPosition, wx.DefaultSize,
                                           0)
        self.m_staticText_pass.Wrap(-1)
        fgSizer_pass.Add(self.m_staticText_pass, 0, wx.ALL, 5)

        self.m_textCtrl_pass = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(120, -1), 0)
        fgSizer_pass.Add(self.m_textCtrl_pass, 0, wx.ALL, 5)

        bSizer2.Add(fgSizer_pass, 1, wx.EXPAND, 5)



        bSizer5.Add(bSizer2, 1, wx.EXPAND, 5)

        bSizer6 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_button1 = wx.Button(self, wx.ID_OK, u"Add", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer6.Add(self.m_button1, 0, wx.ALIGN_CENTER , 1000)

        self.m_button2 = wx.Button(self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer6.Add(self.m_button2, 0, wx.ALIGN_CENTER, 1000)

        # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        bSizer5.Add(bSizer6, 1, wx.EXPAND, 5)

        bSizer1.Add(bSizer5, 1, wx.EXPAND, 5)

        self.SetSizer(bSizer1)
        self.Layout()

        self.Centre(wx.BOTH)

    def add_seconds(self, event):
        seconds_data = {
            '1 hour': 60*60,
            '12 hours': 12*60*60,
            '1 day': 24*60*60,
            '2 days': 48*60*60,
            '3 days': 72*60*60,
            '4 days': 96*60*60,
            '5 days': 120*60*60,
            '7 days': 168*60*60,
            '14 days': 2*168*60*60,
            '30 days': 30*24*60*60,
            'Select...': 0

        }
        self.m_textCtrl7.Clear()
        self.m_textCtrl7.SetValue(str(seconds_data[self.m_comboBox1.GetValue()]))


    def add_event(self):
        url = self.m_url.GetValue()
        #date = self.m_textCtrl5.GetValue()
        #name = self.m_textCtrl6.GetValue()
        name, date = get_event_name_and_date(url)
        interval = self.m_textCtrl7.GetValue()
        notif = self.m_textCtrl8.GetValue()
        row = self.m_textCtrl9.GetValue()
        pwd = self.m_textCtrl_pass.GetValue()
        self.Destroy()
        return {
            'url': url,
            'date':date,
            'name':name,
            'interval':interval,
            'notif_number': notif,
            'row': row,
            'pass': pwd
        }

    def __del__(self):
        pass

class EditEventDialog(wx.Dialog):

    def __init__(self, parent, event):
        self.event = event
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Edit Event", pos=wx.DefaultPosition,
                           size=wx.Size(250, 370), style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        bSizer5 = wx.BoxSizer(wx.VERTICAL)

        bSizer2 = wx.BoxSizer(wx.VERTICAL)

        fgSizer1 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer1.SetFlexibleDirection(wx.BOTH)
        fgSizer1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText4 = wx.StaticText(self, wx.ID_ANY, u"URL:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText4.Wrap(-1)
        fgSizer1.Add(self.m_staticText4, 0, wx.ALL, 5)

        self.m_url = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(200, -1), 0)
        fgSizer1.Add(self.m_url, 0, wx.ALL | wx.EXPAND, 5)

        bSizer2.Add(fgSizer1, 1, wx.EXPAND, 5)

        fgSizer2 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer2.SetFlexibleDirection(wx.BOTH)
        fgSizer2.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText5 = wx.StaticText(self, wx.ID_ANY, u"Date in YYYY-MM-DD", wx.DefaultPosition, wx.DefaultSize,
                                           0)
        self.m_staticText5.Wrap(-1)
        fgSizer2.Add(self.m_staticText5, 0, wx.ALL, 5)

        self.m_textCtrl5 = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(200, -1), 0)
        fgSizer2.Add(self.m_textCtrl5, 0, wx.ALL | wx.EXPAND, 5)

        bSizer2.Add(fgSizer2, 1, wx.EXPAND, 5)

        fgSizer3 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer3.SetFlexibleDirection(wx.BOTH)
        fgSizer3.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText6 = wx.StaticText(self, wx.ID_ANY, u"Event Name", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText6.Wrap(-1)
        fgSizer3.Add(self.m_staticText6, 0, wx.ALL, 5)

        self.m_textCtrl6 = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(200, -1), 0)
        fgSizer3.Add(self.m_textCtrl6, 0, wx.ALL | wx.EXPAND, 5)

        bSizer2.Add(fgSizer3, 1, wx.EXPAND, 5)

        fgSizer4 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer4.SetFlexibleDirection(wx.BOTH)
        fgSizer4.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText7 = wx.StaticText(self, wx.ID_ANY, u"Interval (seconds)", wx.DefaultPosition, wx.DefaultSize,
                                           0)
        self.m_staticText7.Wrap(-1)
        fgSizer4.Add(self.m_staticText7, 0, wx.ALL, 5)

        self.m_textCtrl7 = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(120, -1), 0)
        fgSizer4.Add(self.m_textCtrl7, 0, wx.ALL, 5)

        bSizer2.Add(fgSizer4, 1, wx.EXPAND, 5)

        fgSizer4a = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer4a.SetFlexibleDirection(wx.BOTH)
        fgSizer4a.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_add_sec_button = wx.Button(self, wx.ID_ANY, u"Add Seconds", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_add_sec_button.Bind(wx.EVT_BUTTON, self.add_seconds)
        fgSizer4a.Add(self.m_add_sec_button, 0, wx.ALL, 5)

        m_comboBox1Choices = [u"1 hour", u"12 hours", u"1 day", u"2 days", u"3 days", u"4 days", u"5 days", u"7 days",
                              u"14 days", u"30 days"]
        self.m_comboBox1 = wx.ComboBox(self, wx.ID_ANY, u"Select...", wx.DefaultPosition, wx.DefaultSize,
                                       m_comboBox1Choices, 0)
        fgSizer4a.Add(self.m_comboBox1, 0, wx.ALL, 5)

        bSizer2.Add(fgSizer4a, 1, wx.EXPAND, 5)

        fgSizer5 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer5.SetFlexibleDirection(wx.BOTH)
        fgSizer5.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText8 = wx.StaticText(self, wx.ID_ANY, u"Notification Number", wx.DefaultPosition, wx.DefaultSize,
                                           0)
        self.m_staticText8.Wrap(-1)
        fgSizer5.Add(self.m_staticText8, 0, wx.ALL, 5)

        self.m_textCtrl8 = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(120, -1), 0)
        fgSizer5.Add(self.m_textCtrl8, 0, wx.ALL, 5)

        bSizer2.Add(fgSizer5, 1, wx.EXPAND, 5)

        fgSizer6 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer6.SetFlexibleDirection(wx.BOTH)
        fgSizer6.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText9 = wx.StaticText(self, wx.ID_ANY, u"Ticket Row", wx.DefaultPosition, wx.DefaultSize,
                                           0)
        self.m_staticText9.Wrap(-1)
        fgSizer6.Add(self.m_staticText9, 0, wx.ALL, 5)

        self.m_textCtrl9 = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(120, -1), 0)
        fgSizer6.Add(self.m_textCtrl9, 0, wx.ALL, 5)

        bSizer2.Add(fgSizer6, 1, wx.EXPAND, 5)

        fgSizer_pass = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer_pass.SetFlexibleDirection(wx.BOTH)
        fgSizer_pass.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText_pass = wx.StaticText(self, wx.ID_ANY, u"Pre-sale pass", wx.DefaultPosition, wx.DefaultSize,
                                               0)
        self.m_staticText_pass.Wrap(-1)
        fgSizer_pass.Add(self.m_staticText_pass, 0, wx.ALL, 5)

        self.m_textCtrl_pass = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(120, -1), 0)
        fgSizer_pass.Add(self.m_textCtrl_pass, 0, wx.ALL, 5)

        bSizer2.Add(fgSizer_pass, 1, wx.EXPAND, 5)


        bSizer5.Add(bSizer2, 1, wx.EXPAND, 5)

        bSizer6 = wx.BoxSizer(wx.VERTICAL)

        self.m_button1 = wx.Button(self, wx.ID_OK, u"Add", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer6.Add(self.m_button1, 0, wx.ALL, 5)

        self.m_button2 = wx.Button(self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer6.Add(self.m_button2, 0, wx.ALL, 5)

        bSizer5.Add(bSizer6, 1, wx.EXPAND, 5)

        bSizer1.Add(bSizer5, 1, wx.EXPAND, 5)

        self.SetSizer(bSizer1)
        self.Layout()

        self.Centre(wx.BOTH)
        self.load_data()

    def load_data(self):
        self.m_url.SetValue(self.event[4])
        self.m_textCtrl5.SetValue(self.event[1])
        self.m_textCtrl6.SetValue(self.event[0])
        self.m_textCtrl7.SetValue(self.event[3])
        self.m_textCtrl8.SetValue(self.event[5])
        self.m_textCtrl9.SetValue(self.event[6])
        self.m_textCtrl_pass.SetValue(self.event[10])

    def add_seconds(self, event):
        seconds_data = {
            '1 hour': 60*60,
            '12 hours': 12*60*60,
            '1 day': 24*60*60,
            '2 days': 48*60*60,
            '3 days': 72*60*60,
            '4 days': 96*60*60,
            '5 days': 120*60*60,
            '7 days': 168*60*60,
            '14 days': 2*168*60*60,
            '30 days': 30*24*60*60,
            'Select...': 0

        }
        self.m_textCtrl7.Clear()
        self.m_textCtrl7.SetValue(str(seconds_data[self.m_comboBox1.GetValue()]))

    def add_event(self):
        url = self.m_url.GetValue()
        date = self.m_textCtrl5.GetValue()
        name = self.m_textCtrl6.GetValue()
        interval = self.m_textCtrl7.GetValue()
        notif = self.m_textCtrl8.GetValue()
        row = self.m_textCtrl9.GetValue()
        pwd = self.m_textCtrl_pass.GetValue()
        self.Destroy()
        return {
            'url': url,
            'date':date,
            'name':name,
            'interval':interval,
            'notif_number': notif,
            'row': row,
            'pass': pwd
        }

    def __del__(self):
        pass

