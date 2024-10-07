import sqlite3

from customtkinter import *
from scripts.custom_widgets import *


class Home(CTk):

    """
    Home class, it's a customtkinter window, which asks you for your password and username
    """

    def __init__(self):

        # basic aspects of window

        self.winWidth = 600
        self.winHeight = 500
        super().__init__()
        self.geometry(f'{self.winWidth}x{self.winHeight}+100+100')
        self.title('Home Login')

        # window will not be resizable
        self.resizable(False, False)

        # room number, this will be changed to the login room no.
        self.rmno = None

        # connecting to database

        self.dbcon = sqlite3.connect('database/users.db')
        self.dbcur = self.dbcon.cursor()

        # creating table for first time (incase database was deleted)
        self.dbcur.execute('CREATE TABLE IF NOT EXISTS users(rno char(4) PRIMARY KEY, pwd varchar(24))')

        #adding widgets
        self.add_widgets()

    def run(self):

        """
        simple run program that returns the room number after login

        :return: room number logged into
        """
        self.mainloop()

        return self.rmno

    def add_widgets(self):

        # calling addframe() which adds a frame at the given position and automatically returns it
        # adding images to the homepage

        imageFrame = self.addframe(x=0, y=0, relwidth=0.45, relheight=1)
        imageFrame.addimage('homebg', 270, 500, x=0, y=0, relwidth=1, relheight=1)

        # creating login frame, all the login widgets will be placed here and logo

        loginFrame = self.addframe(relx=0.45, rely=0, relheight=1, relwidth=0.55)
        loginFrame.addimage('logo', 250, 92, relx=0.5, rely=0.05, anchor='n')

        # creating another frame in the login frame to place credentials, easier to position widgets

        cred = loginFrame.addframe(relx=0.5, rely=0.6, relwidth=0.8, relheight=0.55, anchor='center')

        # creating entries for room number and password
        # Entry is a custom class which automatically labels the entries

        self.roomno = Entry(cred, 'Room Number', relx=0.1, rely=0.1)
        self.password = Entry(cred, 'Password', True, relx=0.1, rely=0.4)

        #binding enter key to login command
        self.bind('<Return>', self.login)

        # creating a label to show errors in the credentials

        self.error = CTkLabel(cred, text_color='#ff0000', font=('Arial Italics', 10), text='')
        self.error.place(relx=0.1, rely=0.65)

        # signin button and login button, attacked to their respective commands

        CTkButton(cred, fg_color='#354545', command=self.login, text='Login', corner_radius=2).place(relx=0.05,
                                                                                                     rely=0.95,
                                                                                                     relwidth=0.45,
                                                                                                     relheight=0.15,
                                                                                                     anchor='sw')
        CTkButton(cred, fg_color='#354545', command=self.add_user, text='Sign-Up', corner_radius=2).place(relx=0.95,
                                                                                                          rely=0.95,
                                                                                                          relwidth=0.45,
                                                                                                          relheight=0.15,
                                                                                                          anchor='se')

    def login(self, *args):

        # checking room number and password is entered using 'all' else shows error

        if all([self.roomno.get(), self.password.get()]):

            # checks credentials and destroys window, returning 'mainloop' else shows error

            if self.checkCredentials():
                self.rmno = self.roomno.get()
                self.error.configure(text='')
                self.after(100, self.destroy())
            else:
                self.error.configure(text='Invalid room number/password')
        else:
            self.error.configure(text='Please fill in room number and password')

    # creating a new user, win = the toplevel

    def create_user(self, win, rno, pwd, rct, error):

        self.dbcur.execute('SELECT rno FROM users')
        # getting all users from database
        users = self.dbcur.fetchall()

        """
        checking password validity in order
        1. checking if all the entries are filled using all()
        2. checking if room number already exists by checking db
        3. checking room number format
        4. checking password format
        5. checking if password contains all needed characters, alphabet, number, symbol
        6. checking if password contains only allowed characters
        7. checking if receipt number is valid
        
        if any of these are not right, it will display an error on the label
        """

        errormsg = ''
        if not (all([rno, pwd, rct])):
            errormsg = 'Please enter room number, password and receipt number.'

        elif rno in [usr for usr, in users]: #user, because all values are stored as tuples
            errormsg = 'Room number already registered.'

        elif not (rno[:3].isnumeric() and len(rno) == 4 and rno[3].isalpha() and rno[3].isupper()):
            errormsg = 'Room number is of form "***L" \nWhere * is numeric and L is an alphabet'

        elif not (4 < len(pwd) <= 24):
            errormsg = 'Password must be 5 to 24 characters long.'

        elif not (all([any([i in x for i in pwd.lower()]) for x in ['!@$_', '1234567890', 'qwertyuiopasdfghjklzxcvbnm']])):
            errormsg = 'Password must be contain at least:\none special character, alphabet and number.'

        elif any(i not in ''.join(['!@$_', '1234567890', 'qwertyuiopasdfghjklzxcvbnm']) for i in pwd.lower()):
            errormsg = "Password must not contain characters other than \n!@$_, alphabets and numbers."

        elif not (rct.isnumeric() and len(rct) == 10):
            errormsg = 'Receipt Number must be a 10 digit numeric.'

        error.configure(text=errormsg)

        if not errormsg:

            # adds user and destroys window, closing toplevel
            self.dbcur.execute(f'INSERT INTO users values("{rno}", "{pwd}")')
            self.dbcon.commit()

            win.destroy()


    def add_user(self):

        # creating adduser window
        # basic information
        newUser = CTkToplevel()
        newUser.geometry('300x300+200+200')
        newUser.title('Sign Up')

        # entries for all credentials

        roomno = Entry(newUser, 'Room Number', relx=0.1, rely=0.1)
        password = Entry(newUser, 'New Password', True, relx=0.1, rely=0.35)
        reciept = Entry(newUser, 'Reciept Number', True, relx=0.1, rely=0.6)

        # label for errors

        error = CTkLabel(newUser, text='', text_color='#ff0000', font=('Arial Italics', 8))
        error.place(relx=0.1, rely=0.85)

        # vertical style button to create user

        CTkButton(newUser, text='C\nR\nE\nA\nT\nE', # all values are taken from entries using 'get()' method
                  command=lambda: self.create_user(newUser, roomno.get(), password.get(), reciept.get(), error)).place(
            relx=0.95,
            rely=0.05,
            relheight=0.9,
            relwidth=0.2,
            anchor='ne')

    def addframe(self, **kwargs):

        # adding a new Winframe to the window

        frame = WinFrame(self)
        frame.place(**kwargs)

        return frame

    def checkCredentials(self):

        # checking if username and password match in DB, executes sql query and checking if any columns were returned

        return bool(
            len(
                self.dbcur.execute(
                    f'SELECT * FROM users WHERE rno = "{self.roomno.get()}" AND pwd = "{self.password.get()}"').fetchall()
            )
        )

