from random import Random

from CTkTable import CTkTable
from PIL import Image
from customtkinter import (
    CTkFrame,
    CTkLabel,
    CTkScrollableFrame,
    CTkTabview,
    CTkEntry,
    CTkTextbox,
    CTkCheckBox,
    CTkComboBox,
    CTkImage
)

from scripts.misc import getAsset

"""
 Custom widgets are defined to make it easier to create and use widgets in bulk
 CheckBoxGroup : used to make multiple checkboxes for options, it can return all boxes which are selected
 Entry : automatically labelling the entry and making easier to get and set values, and censoring
 BlockText : paragraph textbox for large amount of characters
 Message : simple chat message for forum page
 Winframe : frame which makes it easier to add images, tables, widgets and other repetitive tasks easily and cleanly
 WinTable : custom table to make access easier
 WinTabView : creates a tab view with a winframe instead of a frame for tabs so that the application works smoothly
"""


class CheckBoxGroup(CTkFrame):

    def __init__(self, root, name, options, width, **kwargs):

        # creating frame

        super().__init__(root, width=width, height=len(options) * 30 + 60)

        # adding label as title

        CTkLabel(self, text=f'{name}', font=('Arial Bold', 15)).place(x=10, y=10)

        # dicionary of checkboxes

        self.options: dict[str:CTkCheckBox] = {}

        # creating checkboxes and placing in frame

        for i, opt in enumerate(options):
            box = CTkCheckBox(self, text=opt)
            box.place(x=10, y=50 + 30 * i)

            self.options[opt] = box

        # placing frame

        self.place(**kwargs)

    def getselected(self):

        """
        gets all selected checkboxes using get() and returns a list of the names of checkboxes
        :return: list
        """

        return [opt for opt in self.options if self.options[opt].get()]

    def clear(self):

        """
        clears all options
        :return: none
        """
        for opt in self.options: self.options[opt].deselect()


class Entry(CTkFrame):

    def __init__(self, root, name, censoring=False, width=150, **kwargs):
        # creating frame and adding title

        super().__init__(root, width=width, height=70, fg_color='transparent')
        CTkLabel(self, text=f'{name}:', font=('Arial Bold', 15)).place(x=10, y=10)

        # creating entry and checking for censoring

        self.entry = CTkEntry(self, width=width - 20)
        self.entry.place(x=10, y=40)

        self.censoring = not censoring
        self.place(**kwargs)

        self.togglecensoring()

    def togglecensoring(self):
        # turns on or off censoring
        self.entry.configure(show='' if self.censoring else '*')
        self.censoring = not self.censoring

    def get(self):
        # gets values of entry
        return self.entry.get()

    def clear(self):
        # clears entry
        self.entry.delete('0', 'end')


class Message(CTkFrame):

    def __init__(self, master, width, room, date, content):
        # creating frame
        super().__init__(master, width=width)

        # creating a random color which remains same for same user, using random.Random seeds
        color_rand = Random(int(room[:3]))

        # creating user, content and date content is made to wrap around width, minimum width is 90px

        d = CTkLabel(self, text=f"Room {room}", font=('Calibri Bold', 11),
                     text_color='#' + ''.join((hex(color_rand.randint(130, 255))[2:] for i in range(3))), width=90,
                     anchor='w')
        d.pack(anchor='w', pady=1, padx=5)

        con = CTkLabel(self, wraplength=width, text=content, font=('Arial Bold', 14), justify='left')
        con.pack(anchor='w', after=d, padx=8, pady=5)

        t = CTkLabel(self,
                     text=f"{'/'.join(date.split()[0].split('-')[:0:-1])}  " + ':'.join(date.split()[1].split(':')[:2]),
                     font=('Calibri Bold', 8), anchor='w')
        t.pack(anchor='e', pady=1, padx=5, after=con)
        self.pack_propagate()


class BlockText(CTkFrame):
    def __init__(self, root, name, width, height, m=None, **kwargs):

        # creating frame and placing title lable
        super().__init__(root, width=width, height=height, fg_color='transparent')
        CTkLabel(self, text=f'{name}:', font=('Arial Bold', 15)).place(x=10, y=10)

        # declaring limit, text cannot exceed this many characters
        self.limit = m

        # creating textbox and placing it
        self.text = CTkTextbox(self, width=width - 20, height=height - 50)
        self.text.place(x=10, y=40)

        self.old_value = ''

        # binding keypress to the char limit checking function
        self.text.bind('<KeyPress>', self.check_limit)

        self.place(**kwargs)

    def check_limit(self, event):

        # if limit exists. checks character limit, and if exceeded, reverts to prvs value

        if not self.limit: return
        t = self.get()
        if len(t) > self.limit:
            self.clear()
            self.text.insert(0.0, self.old_value)
        else:
            self.old_value = t.strip()

    def get(self):

        # getting entry
        return self.text.get('0.0', 'end')

    def clear(self):

        # clearing entry
        self.text.delete('0.0', 'end')


class WinFrame(CTkFrame):

    def __init__(self, *args, **kwargs):
        # creating simple frame
        super().__init__(*args, **kwargs)

    def addframe(self, width=200, height=200, **kwargs):
        # adds another frame inside current frame
        frame = WinFrame(self, width, height)
        frame.place(**kwargs)
        return frame

    def createchoice(self, name, options, **kwargs):
        # creates a combobox with a title to choose from values and returns the combo box
        frame = CTkFrame(self, width=200, height=90)
        CTkLabel(frame, text=f'Choose {name}', font=('Calibri Bold', 20)).place(x=10, y=10)
        combo = CTkComboBox(frame, values=options, width=180, font=('Calibri Bold', 14))
        combo.place(x=10, y=50)

        frame.place(**kwargs)
        return combo

    def createtable(self, title, columns, width, height, values, **kwargs):
        # creates a table with a title, and titled columns and returns it

        # creating a scrollable frame so that multiple valyues can be inserted
        frame = CTkScrollableFrame(self, width, height)
        frame.place(**kwargs)

        label = CTkLabel(frame, text=title, font=('Calibri Bold', 24))
        label.pack(padx=10, pady=10, )
        table = CTkTable(frame,
                         column=len(columns),
                         row=len(values) + 1,
                         values=[[i.title() for i in list(columns)]] + values,
                         width=(width - 20 - len(columns) * 1) / len(columns))
        table.pack()
        return table

    def addimage(self, name, width, height, **kwargs):
        # adds an image by taking its filename

        img = CTkImage(Image.open(getAsset('image', name)), size=(width, height))
        imagelabel = CTkLabel(self, image=img, text='')
        imagelabel.place(**kwargs)

        return imagelabel


class WinTabView(CTkTabview):

    def __init__(self, *args, **kwargs):
        # creates simple tab view
        super().__init__(*args, **kwargs)

    def add_tab(self, name):
        # setting tab as winframe
        self.add(name)

        self._tab_dict[name] = WinFrame(self,
                                        height=0,
                                        width=0,
                                        border_width=0,
                                        corner_radius=0)

        return self._tab_dict[name]

    def tab(self, name: str) -> WinFrame:
        """ returns reference to the tab with given name """

        if name in self._tab_dict:
            return self._tab_dict[name]
        else:
            raise ValueError(f"CTkTabview has no tab named '{name}'")
