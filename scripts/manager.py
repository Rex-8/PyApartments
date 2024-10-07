import json
import sqlite3
from datetime import date, datetime

from customtkinter import *
from tkcalendar import Calendar

from scripts.custom_widgets import WinFrame, WinTabView, Entry, BlockText, CheckBoxGroup, Message


class Manager(CTk):
    """
    A class to create the management app, so that the user can manage their apartment
    """

    def __init__(self, room_number):

        # creating window with basic information
        super().__init__()
        self.geometry('700x500+100+100')
        self.title(f'Room {room_number} Management')

        self.room_number = room_number

        # creating a tab view

        self.options = WinTabView(self, width=680, height=480)
        self.options.place(x=10, y=10)

        # creating a tab for all the options for apartment management

        for tab in ['Home', 'Complaints', 'Services', 'Forum']:
            self.options.add_tab(tab)

        # creating dctionary to story widgets which might be used

        self.complaints = {}
        self.services = {}
        self.forum = {}

        # connecting to db and making required tables

        self.dbcon = sqlite3.connect('database/manager_dat.db')
        self.dbcur = self.dbcon.cursor()

        self.dbcur.execute(
            'CREATE TABLE IF NOT EXISTS requests(type varchar(20), room char(4), date datetime, req varchar(20))')
        self.dbcur.execute(
            'CREATE TABLE IF NOT EXISTS services(service varchar(20), room char(4), date datetime, sched datetime, call bool)')
        self.dbcur.execute('CREATE TABLE IF NOT EXISTS forum(room char(4), date datetime, con varchar(200))')

        self.dbcon.commit()

        self.requestHistory = []

        self.build_tabs()
        self.mainloop()

    def addframe(self, width=100, height=100, **kwargs):

        # creating new winframe

        frame = WinFrame(self, width, height)
        frame.place(**kwargs)

        return frame

    def build_tabs(self):

        # Building Home Tab

        # getting recent requests from db and creating table

        self.dbcur.execute(f'SELECT date, type, req FROM requests WHERE room = "{self.room_number}"')

        self.service_table = self.options.tab('Home').createtable(f'Service History for Room {self.room_number}',
                                                                  ['date', 'type', 'request'],
                                                                  400, 300,
                                                                  list(self.dbcur.fetchall())[::-1],
                                                                  # more recent requests come first
                                                                  relx=0.5, rely=0.1, anchor='n')

        # Building Complaints Tab

        # creating label
        CTkLabel(self.options.tab('Complaints'), text='Register Complaint.', font=('Calibri Bold', 24)).place(relx=0.5,
                                                                                                              y=10,
                                                                                                              anchor='n')

        # creating entries and textblock
        self.complaints['sub'] = Entry(self.options.tab('Complaints'), 'Subject', width=450, x=10, y=40)
        self.complaints['con'] = BlockText(self.options.tab('Complaints'), 'Description', width=450, height=300, x=10,
                                           y=120)

        # check box group for type of complaint
        self.complaints['cat'] = CheckBoxGroup(self.options.tab('Complaints'), 'Categories',
                                               ['Service', 'Maintenance', 'Noise', 'Pest', 'Other'], 190, x=470, y=40)

        # button to register complaint
        self.complaints['but'] = CTkButton(self.options.tab('Complaints'), command=self.register_complaint,
                                           text='Register', font=('Arial Bold', 24), width=190, height=50,
                                           fg_color='#354545').place(x=470, y=400, anchor='sw')

        # Building Complaints Tab

        CTkLabel(self.options.tab('Services'),
                 text='Request Services.',
                 font=('Calibri Bold', 24)
                 ).place(relx=0.5, y=10, anchor='n')

        # choice of what service is required

        self.services['ser'] = self.options.tab('Services').createchoice('Service',
                                                                         ['Plumbing', 'Electrician', 'Cleaning',
                                                                          'Technician'], x=10, y=50)

        # creating a frame for calendar
        f = self.options.tab('Services').addframe(x=230, y=50, width=440, height=370)
        CTkLabel(f, text='Choose Date:', font=('Calibri Bold', 20)).place(x=10, y=10)
        # calendar to choose date
        self.services['cal'] = Calendar(f, width=920, height=640, date_pattern='mm/dd/y', font=('Calibri', 16),
                                        mindate=datetime.now())
        self.services['cal'].place(relx=0.5, y=50, anchor='n')

        # logo of cleaning service
        self.options.tab('Services').addimage('pyclean', 150, 150, x=110, y=150, anchor='n')

        # checkbox to call
        self.services['che'] = CTkCheckBox(self.options.tab('Services'), text='Call Prior?')
        self.services['che'].place(x=10, y=325)

        # button to request service
        CTkButton(self.options.tab('Services'), text='Schedule', font=('Calibri Bold', 20),
                  command=self.request_service, width=200, height=40).place(x=10, y=370)

        # Building Forum Tab

        CTkLabel(self.options.tab('Forum'),
                 text='Chat with Members',
                 font=('Calibri Bold', 24)
                 ).place(x=505, y=10, anchor='n')

        # creating textbox for message content, 200 word limit
        self.forum['con'] = BlockText(self.options.tab('Forum'), 'Content', m=199, width=350, height=370, x=10,
                                      y=10)

        # send button invokes send message function

        CTkButton(self.options.tab('Forum'), text='Send', font=('Calibri Bold', 20), command=self.send_message,
                  width=330, height=40).place(x=20, y=385)

        # getting messages from forum
        self.dbcur.execute(f'SELECT room, date d, con FROM forum where strftime("%Y", d) = strftime("%Y", date())')

        # creatin a scrollable frame to put chat messages
        self.forum['chatbox'] = CTkScrollableFrame(self.options.tab('Forum'), width=290, height=365)
        self.forum['chatbox'].place(x=360, y=50)
        for i, message in enumerate(self.dbcur.fetchall()):
            # putting messages in for each message
            Message(self.forum['chatbox'], 200, *message).pack(expand=True,
                                                               anchor='e' if message[0] == self.room_number else 'w',
                                                               pady=10)

        # when chatbox comes onto screen, it scrolls down to the bottom
        self.forum['chatbox'].bind('<Visibility>', lambda e: self.forum['chatbox']._parent_canvas.yview_moveto(1.0))

    def send_message(self):

        # sends a message in chat, and record it in db, also adds a message to the frame
        self.dbcur.execute(
            f'INSERT INTO forum values("{self.room_number}", datetime(), "{self.forum["con"].get().strip()}")')
        self.dbcon.commit()

        Message(self.forum['chatbox'], 200, self.room_number, datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                self.forum["con"].get().strip()).pack(expand=True, anchor='e', pady=10)
        self.forum['con'].clear()
        self.forum['chatbox'].after(10, self.forum['chatbox']._parent_canvas.yview_moveto, 1.0)

    def request_service(self):

        # requests a service, by adding it to DB and adding to recents
        m, d, y = (int(i) for i in self.services['cal'].get_date().split('/'))
        service = self.services['ser'].get()

        self.dbcur.execute(f'INSERT INTO requests values("service", "{self.room_number}", date(), "{service}")')
        self.dbcur.execute(
            f'INSERT INTO services values("{service}", "{self.room_number}", date(), "{date(y, m, d)}", {str(bool(self.services["che"].get())).lower()})')

        self.dbcon.commit()

        self.service_table.add_row([datetime.now().strftime('%Y-%m-%d'), 'service', service])

    def register_complaint(self):

        # registers complaint by adding to json db and adding to recents
        with open('database/complaints.json') as c:
            complaints = json.load(c)

        complaints[f"c{len(complaints)}"] = {
            'room': self.room_number,
            'cat': self.complaints['cat'].getselected(),
            'sub': self.complaints['sub'].get(),
            'con': self.complaints['con'].get()
        }

        for w in ['sub', 'cat', 'con']:
            self.complaints[w].clear()

        json.dump(complaints, open('database/complaints.json', 'w'))
        self.dbcur.execute(f'INSERT INTO requests values("complaint", "{self.room_number}", date(), "-")')
        self.dbcon.commit()

        # addrow is used to add to recents table
        self.service_table.add_row([datetime.now().strftime('%Y-%m-%d'), 'complaint', '-'])
