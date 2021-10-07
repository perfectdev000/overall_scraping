# https://wxpython.org/Phoenix/docs/html/wx.dataview.DataViewCtrl.html
# https://wxpython.org/Phoenix/docs/html/wx.lib.mixins.listctrl.ColumnSorterMixin.html
import locale
import pickle
import re
import smtplib
import threading
import time
import webbrowser
from datetime import datetime
from operator import itemgetter
from pprint import pprint

import wx
import wx.xrc
import wx.dataview
import wx.lib.mixins.listctrl as listmix
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from gui_dialogs import AddEventDialog, SettingsDialog, EditEventDialog
from scrapers import check_website


###########################################################################
 

class TestListCtrl(wx.ListCtrl):

    # ----------------------------------------------------------------------
    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)


###########################################################################
class LowNumberApp(wx.Frame, listmix.ColumnSorterMixin):
    def __init__(self, parent):
        self.event_data = {}
        #self.save_event_data() # When you want to create new data file
        with open('settings.pickle', 'rb') as f:
            self.settings = pickle.load(f)
        self.master = MasterList(self.settings['MasterURL'])
        # with open('timestamps.pickle', 'rb') as f:
        #     self.event_timestamps = pickle.loads(f)
        self.event_timestamps = {}
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition,
                              size=wx.Size(1000, 700), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer2 = wx.BoxSizer(wx.VERTICAL)

        bSizer6 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_button_update = wx.Button(self, wx.ID_ANY, u"Quick Check", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_button_update.Bind(wx.EVT_BUTTON, self.update_event)
        bSizer6.Add(self.m_button_update, 0, wx.ALL, 5)

        self.m_button_start = wx.Button(self, wx.ID_ANY, u"Start", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_button_start.Bind(wx.EVT_BUTTON, self.start)
        bSizer6.Add(self.m_button_start, 0, wx.ALL, 5)

        self.m_gauge1 = wx.Gauge(self, wx.ID_ANY, 100, wx.DefaultPosition, wx.Size(300, 25), wx.GA_HORIZONTAL)
        self.m_gauge1.SetValue(0)
        bSizer6.Add(self.m_gauge1, 0, wx.ALL, 5)

        self.m_comboBox10 = wx.ComboBox(self, wx.ID_ANY, u"Capmonster", wx.DefaultPosition, wx.Size(120, 25), [u'Capmonster', u'Anticaptcha'], 0)
        bSizer6.Add(self.m_comboBox10, 0, wx.ALL, 5)

        self.m_comboBox1 = wx.ComboBox(self, wx.ID_ANY, u"Sort Column...", wx.DefaultPosition, wx.Size(120, 25), [u'Date', u'Added on', u'Last Check', 'Quantity'], 0)
        bSizer6.Add(self.m_comboBox1, 0, wx.ALL, 5)

        self.m_button_sort_up = wx.Button(self, wx.ID_ANY, u"↑", wx.DefaultPosition, wx.Size(25,25), 0)
        self.m_button_sort_up.Bind(wx.EVT_BUTTON, self.sort_up)
        bSizer6.Add(self.m_button_sort_up, 0, wx.ALL, 5)

        self.m_button_sort_down = wx.Button(self, wx.ID_ANY, u"↓", wx.DefaultPosition, wx.Size(25,25), 0)
        self.m_button_sort_down.Bind(wx.EVT_BUTTON, self.sort_down)
        bSizer6.Add(self.m_button_sort_down, 0, wx.ALL, 5)

        bSizer2.Add(bSizer6, 0, wx.ALL, 5)

        bSizer3 = wx.BoxSizer(wx.HORIZONTAL)

        # Buttons

        self.m_button_add = wx.Button(self, wx.ID_ANY, u"Add Event", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_button_add.Bind(wx.EVT_BUTTON, self.add_event)
        bSizer3.Add(self.m_button_add, 0, wx.ALL, 5)

        self.m_button_edit = wx.Button(self, wx.ID_ANY, u"Edit Event", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_button_edit.Bind(wx.EVT_BUTTON, self.edit_event)
        bSizer3.Add(self.m_button_edit, 0, wx.ALL, 5)

        self.m_button_remove = wx.Button(self, wx.ID_ANY, u"Remove Event", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_button_remove.Bind(wx.EVT_BUTTON, self.remove_event)
        bSizer3.Add(self.m_button_remove, 0, wx.ALL, 5)

        self.m_button_settings = wx.Button(self, wx.ID_ANY, u"Settings", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_button_settings.Bind(wx.EVT_BUTTON, self.edit_settings)
        bSizer3.Add(self.m_button_settings, 0, wx.ALL, 5)

        self.m_button_master = wx.Button(self, wx.ID_ANY, u"Master List", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_button_master.Bind(wx.EVT_BUTTON, self.master_list)
        bSizer3.Add(self.m_button_master, 0, wx.ALL, 5)

        bSizer2.Add(bSizer3, 0, wx.ALL, 5)

        # List Control
        self.list_ctrl = TestListCtrl(self, size=(-1, 1500),
                                      style=wx.LC_REPORT
                                            | wx.BORDER_SUNKEN
                                            | wx.LC_SORT_ASCENDING
                                            | wx.LC_REPORT
                                      )
        self.list_ctrl.InsertColumn(0, "Event Name")
        self.list_ctrl.SetColumnWidth(0, 400)
        self.list_ctrl.InsertColumn(1, "Date", wx.LIST_FORMAT_RIGHT)
        self.list_ctrl.InsertColumn(2, "Quantity")
        self.list_ctrl.InsertColumn(3, "Interval")
        self.list_ctrl.InsertColumn(4, 'URL')
        self.list_ctrl.InsertColumn(5, "Notification")
        self.list_ctrl.InsertColumn(6, 'Row')
        self.list_ctrl.InsertColumn(7, 'Added on')
        self.list_ctrl.InsertColumn(8, 'Last Check')
        self.list_ctrl.InsertColumn(9, 'Cart Timer')
        self.list_ctrl.InsertColumn(10, 'Pre-sale pass')
        bSizer2.Add(self.list_ctrl, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(bSizer2)
        self.Layout()

        self.Centre(wx.BOTH)
        self.load_data_to_list_ctrl()
    # Threading
    def startThread(self, event):
        th = threading.Thread(target=self.start, args=(event,))
        th.start()
    def stopThread(self, event):
        self.shutdown_event.set()
    # Button methods
    def sort_up(self, event):
        self.sort_by_date(True)
    def sort_down(self, event):
        self.sort_by_date(False)
    def sort_by_date(self, ascending):
        if self.m_comboBox1.GetValue() == 'Sort Column...':
            return
        column_indexes = {
            'Date': 1,
            'Added on': 7,
            'Last Check': 8,
            'Quantity': 2
        }
        column_idx = column_indexes[self.m_comboBox1.GetValue()]


        print("Sorting by column:", self.m_comboBox1.GetValue())
        data_lst = []
        data_lst2 = []
        if column_idx == 2:
            for key, data in self.event_data.items():
                if data[column_idx] == '-':
                    dat = list(data)
                    dat[column_idx] = 0
                    data = tuple(dat)
                data_lst.append(data)
            data_lst.sort(key=itemgetter(1), reverse=True)
            data_lst.sort(key=lambda L: int(L[column_idx]))

            for d in data_lst:
                if 0 == d[column_idx]:
                    dat = list(d)
                    dat[column_idx] = '-'
                    d = tuple(dat)
                data_lst2.append(d)

            if not ascending:
                data_lst2.reverse()

        else:
            for key, data in self.event_data.items():
                if data[column_idx] == '-':
                    dat = list(data)
                    dat[column_idx] = '1900-01-01'
                    if column_idx == 8:
                        dat[column_idx] += ' 00:00'
                    data = tuple(dat)
                data_lst.append(data)

            data_lst.sort(key=itemgetter(1), reverse=True)

            date_format = "%Y-%m-%d"
            if column_idx == 8:
                date_format += ' %H:%M'
            data_lst.sort(key=lambda L: datetime.strptime(L[column_idx], date_format))

            for d in data_lst:
                if '1900-01-01' in d[column_idx]:
                    dat = list(d)
                    dat[column_idx] = '-'
                    d = tuple(dat)
                data_lst2.append(d)

            if not ascending:
                data_lst2.reverse()

        self.event_data = {}
        for i, data in enumerate(data_lst2, 1):
            self.event_data[i] = data

        self.save_event_data()
        self.load_data_to_list_ctrl()

    def start(self, event):
        if self.m_button_start.LabelText == "Start":
            self.m_gauge1.Pulse()
            self.m_button_start.SetLabel("Stop")
            self.th = threading.Thread(target=self.update_gui)
            self.th.start()
        elif self.m_button_start.LabelText == "Stop":
            self.m_gauge1.SetValue(0)
            self.m_button_start.SetLabel("Start")

    def update_gui(self):
        self.shutdown_event = threading.Event()
        while True:
            for key, value in self.event_data.items():
                url = value[4]
                if url in self.event_timestamps.keys():
                    interval = int(value[3])
                    current_time = time.time()
                    last_time_check = self.event_timestamps[url]
                    if current_time - last_time_check <= interval:
                        continue

                if self.m_button_start.LabelText == "Start":
                    self.shutdown_event.set()
                    break

                print('checking tickets for', value[0])
                checker = check_website(url, self.settings['Proxy'], value[6], value[10])
                qty, timer = checker.check_ticket_qty()
                timer_str = "Yes" if timer else "No"
                print(f">>>>>>>>>>>>>>>>>>{qty}<<<<<<<<<<<<<<<<<<{timer}")
                evt_data = (value[0], value[1], str(qty), value[3], value[4], value[5], value[6], value[7],
                                        datetime.today().strftime('%Y-%m-%d %H:%M'), timer_str, value[10])
                
                time.sleep(0.5)
                self.event_data[key] = evt_data
                self.save_event_data()
                self.load_data_to_list_ctrl()
                self.event_timestamps[url] = time.time()
                self.master.add_to_list(evt_data)

    def update_event(self, event):
        self.th = threading.Thread(target=self.update_event_action)
        self.th.start()

    def update_event_action(self):
        # self.m_button_update.Disable()
        self.shutdown_event = threading.Event()
        captch_way = self.m_comboBox10.GetValue()
        selected = self.list_ctrl.GetFirstSelected()
        if selected >= 0:
            url = self.list_ctrl.GetItemText(selected, 4)
            data_key = None
            for key, value in self.event_data.items():
                if value[4] == url:
                    data_key = key
                    print('checking tickets for', value[0], url)
                    checker = check_website(url, self.settings['Proxy'], value[6], value[10])
                    qty, timer = checker.check_ticket_qty(captch_way)
                    if timer is None:
                        timer_str = '-'
                    else:
                        timer_str = "Yes" if timer else "No"
                    evt_data = (
                    value[0], value[1], str(qty), value[3], value[4], value[5], value[6], value[7],
                    datetime.today().strftime('%Y-%m-%d %H:%M'), timer_str, value[10])
                    self.event_data[key] = evt_data
                    self.save_event_data()
                    self.load_data_to_list_ctrl()
                    #     self.m_button_update.Enable()
                    self.check_to_send_email(self.event_data[key])
                    self.master.add_to_list(evt_data)
                    break

    def edit_event(self, event):
        selected = self.list_ctrl.GetFirstSelected()
        if selected >= 0:
            url = self.list_ctrl.GetItemText(selected, 4)
            data_key = None
            for key, value in self.event_data.items():
                if value[4] == url:
                    data_key = key
                    break

            dlg = EditEventDialog(self, value)
            if dlg.ShowModal() == wx.ID_OK:
                data = dlg.add_event()
                url = data['url']
                date = data['date']
                name = data['name']
                interval = data['interval']
                notif = data['notif_number']
                ticket_row = data['row']
                presale = data['pass']

                evt_data = (name, date, value[2], interval, url, notif, ticket_row, value[7], value[8], value[9], presale)
                self.event_data[key] = evt_data
                self.save_event_data()
                self.load_data_to_list_ctrl()
                self.master.update_list(evt_data)

    def fix_ids(self):
        events = {}
        i = 1
        for key, value in self.event_data.items():
            events[i] = value
            i += 1
        return events

    def remove_event(self, event):
        selected = self.list_ctrl.GetFirstSelected()
        print(selected)
        if selected >= 0:
            url = self.list_ctrl.GetItemText(selected, 4)
            data_key = None
            for key, value in self.event_data.items():
                if value[4] == url:
                    data_key = key
                    break
            self.event_data.pop(data_key)
            self.event_data = self.fix_ids()
            self.save_event_data()
            self.load_data_to_list_ctrl()
            self.master.remove_from_list(url)

    def add_event(self, event):
        dlg = AddEventDialog(self)
        # print("add event button clickentd")
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.add_event()
            url = data['url']
            date = data['date']
            name = data['name']
            interval = data['interval']
            notif = data['notif_number']
            ticket_row = data['row']
            presale = data['pass']
            date_created = datetime.today().strftime('%Y-%m-%d')
            # print(self.event_data)
            evt_dat = (
            name, date, '-', interval, url, notif, ticket_row, date_created, "-", '-', presale)
            self.event_data[len(self.event_data.keys()) + 1] = evt_dat
            self.save_event_data()
            self.load_data_to_list_ctrl()
            self.master.add_to_list(evt_dat)
        dlg.Destroy()

    def edit_settings(self, event):
        dlg = SettingsDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.settings = dlg.get_data()
            with open('settings.pickle', 'wb+') as f:
                pickle.dump(self.settings, f)

    def master_list(self, event):
        webbrowser.open(self.settings['MasterURL'])

    #############################################

    def load_event_data(self):
        # with open('data.pickle', 'wb') as f:
        #     pickle.dump({}, f)
        with open('data.pickle', 'rb') as f:
            self.event_data = pickle.load(f)


    def save_event_data(self):
        with open('data.pickle', 'wb') as f:
            pickle.dump(self.event_data, f)

    def load_data_to_list_ctrl(self):
        self.list_ctrl.DeleteAllItems()
        self.load_event_data()

        for x in list(self.event_data.keys()):
            self.list_ctrl.InsertItem(10000, '')

        index = 0
        for key, data in self.event_data.items():
           # index = key - 1
            self.list_ctrl.SetItem(index, 0, data[0])
            self.list_ctrl.SetItem(index, 1, data[1])
            self.list_ctrl.SetItem(index, 2, data[2])
            self.list_ctrl.SetItem(index, 3, data[3])
            self.list_ctrl.SetItem(index, 4, data[4])
            self.list_ctrl.SetItem(index, 5, data[5])
            self.list_ctrl.SetItem(index, 6, data[6])
            self.list_ctrl.SetItem(index, 7, data[7])
            self.list_ctrl.SetItem(index, 8, data[8])
            self.list_ctrl.SetItem(index, 9, data[9])
            self.list_ctrl.SetItem(index, 10, data[10])
            self.list_ctrl.SetItemData(index, key)
            index += 1

        self.itemDataMap = self.event_data
        listmix.ColumnSorterMixin.__init__(self, 5)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick, self.list_ctrl)

    def GetListCtrl(self):
        return self.list_ctrl

        # ----------------------------------------------------------------------

    def OnColClick(self, event):
        event.Skip()

    def ListCompareFunction(self, item1, item2):
        dt1 = datetime.strptime(item1, "%Y-%m-%d")
        dt2 = datetime.strptime(item2, "%Y-%m-%d")
        if dt1 == dt2:
            return 0
        elif dt1 < dt2:
            return -1
        elif dt1 > dt2:
            return 1

    def check_to_send_email(self, event):
        try:
            current_amount = int(event[2])
        except ValueError:
            return False
        if current_amount <= int(event[5]):
            sub = "Ticket Low Number notification for " + event[0]
            msg = "Event Name: {}\nEvent URL: {}\nEvent Date: {}\nTicket Quantity: {}\n".format(
                event[0], event[4], event[1], event[2]
            )
            if int(event[2]) > 0 and int(event[2]) < 5000:
                self.send_email(msg, sub)

    def send_email(self, message, subject, retry=0):
        server = smtplib.SMTP('smtp.gmail.com', 587)
        try:
            server.starttls()
        except Exception as e:
            if retry == 10:
                print('falied with', e)
                return
            retry += 1
            return self.send_email(message, subject, retry)
        server.login(self.settings['GmailEmail'], self.settings['GmailPass'])
        msg = "Subject: {}\n\n{}".format(subject, message)
        msg = msg.encode()

        print('sending to', self.settings['NotifyEmail'])
        try:
            server.sendmail(self.settings['GmailEmail'], self.settings['NotifyEmail'], msg)
        except UnicodeEncodeError:
            pass
        time.sleep(1)
        server.quit()

    def __del__(self):
        pass


class MasterList(object):
    def __init__(self, sheet_url):
        self.sheet = sheet_url
        if sheet_url:
            scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
            credentials = ServiceAccountCredentials.from_json_keyfile_name('mastelistevents-0050cd80b07f.json', scope)
            gc = gspread.authorize(credentials)
            self.sheet = gc.open_by_url(sheet_url).get_worksheet(0)
        #print(self.sheet.get_all_records())

    def add_to_list(self, event, retry=0):
        if self.sheet:

            try:
                row = len(self.sheet.get_all_values())+1
            except:
                if retry == 10:
                    return
                retry += 1
                self.reconnect()
                time.sleep(1)
                return self.add_to_list(event, retry)
            print('Adding event to Google sheet...')
            for idx, val in enumerate(event, 1):
                self.sheet.update_cell(row, idx, val)

    def update_list(self, event):
        print('Updating event on Google sheet...')
        if self.sheet:
            try:
                cell = self.sheet.find(event[4])
            except:
                return
            for idx, val in enumerate(event, 1):
                self.sheet.update_cell(cell.row, idx, val)

    def remove_from_list(self, url):
        if self.sheet:
            print('Removing event from Google sheet...')
            for i in range(30):
                try:
                    cell = self.sheet.find(url)
                    self.sheet.delete_row(cell.row)
                except:
                    break
        #print(cell.row)

    def reconnect(self):
        if self.sheet:
            scope = ['https://spreadsheets.google.com/feeds',  'https://www.googleapis.com/auth/drive']
            credentials = ServiceAccountCredentials.from_json_keyfile_name('mastelistevents-0050cd80b07f.json', scope)
            gc = gspread.authorize(credentials)
            self.sheet = gc.open_by_url(self.sheet).get_worksheet(0)

if __name__ == "__main__":
    app = wx.App(False)
    frame = LowNumberApp(None)
    frame.Show(True)
    # start the applications
    app.MainLoop()
