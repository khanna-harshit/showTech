# imported packages
from kivy.app import App
import datetime
from kivy.uix.label import Label
import tarfile
import os
import re
from kivy.properties import ObjectProperty
from kivy.uix.button import Button
from kivy.clock import Clock, mainthread
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooser
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
import pymongo
from kivy.lang import Builder
from pymongo import MongoClient
from kivy.uix.dropdown import DropDown
import kivy
from kivy.config import Config


# ----------------------------------------------------------------------------------------------------------------
kivy.require('1.9.0')

kivy.config.Config.set('graphics','resizable', True)

Config.write()


# python module to set the color to cream

Window.clearcolor = (164 / 255, 163 / 255, 167 / 255, 0.83)



# -----------------------------------------------------------------------------------------------------------------

# The screen manager is a widget dedicated to managing multiple screens for application.
class Manager(ScreenManager):
    pass


# ------------------------------------------------------------------------------------------------------------------

# Analyse scren shown when the user click on analyse button.
# screen seen only for 8 seconds.
class Analyse(Screen):
    pass


# ------------------------------------------------------------------------------------------------------------------

# Result Screen Where analysis shown
class Results(Screen):

    # Button "Back" in the result screen which when clicked screen move to "first" screen
    def ChangeFromResultsToMyLayout(self):
        kv.current = 'MyLayout'


# ------------------------------------------------------------------------------------------------------------------

# screen used to upload a file using filechooser
# show when click on "upload file" button
class MyPopup(Screen):

    # Button "Upload" in MyPopup screen which when clicked move screen to "first" screen
    def ChangeFromPopupToMyLayout(self):
        kv.current = 'MyLayout'

    # Used to change the text from "no file choosen" to "file_name"
    def upload(self, filename, filepath):
        my_layout = self.manager.get_screen('MyLayout')
        try:
            my_layout.ids.file_choosen.text = filename[0]
        except:
            pass


# -----------------------------------------------------------------------------------------------------------------


# First Screen
class MyLayout(Screen):

    # function called when click on "analyse" button
    def analyse_text(self):
        # text written is Empty
        if self.ids.text_input.text == '':
            self.ids.text_input.text = ''
        else:
            try:
                # creation of MongoClient
                client = MongoClient()
                # Connect with the portnumber and host
                client = MongoClient("mongodb://localhost:27017/")
                db = client["ShowTechAnalyser"]
                collection = db["Data"]
                now = datetime.datetime.now()
                # insert the data with time
                db.collection.insert_one({'contents': self.ids.text_input.text, 'time': now})
                self.ids.text_input.text = ''
                # changing screen from "MyLayout" to "Analyse"
                kv.current = 'Analyse'
                # clock time of 8 sec screen
                Clock.schedule_once(self.switch, 8)
                # result shown in "Results" Screen with the data fetch from database with the help of time
                results = self.manager.get_screen('Results')
                data = db.collection.find_one({'time': now})
                lst = data['contents'].split('\n')
                s = '\n'.join(lst)
                results.ids.result.text = '[b]' + s + '[/b]'

            except:
                pass

    # called in line number 96
    def switch(self, *args):
        kv.current = "Results"

    # use to reset text to empty
    def reset_text(self):
        self.ids.text_input.text = ''

    # use to reset file to "no file choosen"

    def reset_file(self):
        self.ids.file_choosen.text = 'no file choosen'

    # use to analyse file

    def analyse_file(self):
        # clock time of 8 sec screen will change to results

        if self.ids.file_choosen.text != 'no file choosen':

            # getting teh path of file
            kv.current = 'Analyse'
            Clock.schedule_once(self.switch, 8)
            path = self.ids.file_choosen.text
            file = tarfile.open(path)
            file_name = file.getnames()
            now = datetime.datetime.now()
            dump_files = []
            for i in range(1, len(file_name) - 1):
                file_name_split = file_name[i].split('/')
                if file_name_split[1] == 'dump':
                    dump_files.append(file_name[i])
            file.extractall('C:/Users/in68700007/Desktop/sonic')
            file.close()
            insert = []
            for i in dump_files:
                f = open("sonic" + '/' + i, 'r')
                text = f.read()
                path_list = i.split('/')
                file_name = ''
                temp_name = path_list[-1]
                temp_name_list = temp_name.split('.')
                for j in range(0, len(temp_name_list)):
                    if j == len(temp_name_list) - 1:
                        file_name = file_name + temp_name_list[j]
                    else:
                        file_name = file_name + temp_name_list[j] + " "
                insert.append({'path': 'sonic' + '/' + i, 'name': "show " + file_name, 'contents': text, 'time': now})
            # connect with database

            client = MongoClient()
            # Connect with the port number and host

            client = MongoClient("mongodb://localhost:27017/")
            db = client["ShowTechAnalyser"]
            collection = db["Data"]

            # Get the list of all files and directories
            # adding all the files to the database

            self.ids.file_choosen.text = 'no file choosen'

            # changing the screen from "MyLayout" to "Analyse"

            results = self.manager.get_screen('Results')

            db.collection.insert_many(insert)

            # result shown in "Results" Screen with the data fetch from database with the help of time

            data = list(db.collection.find({'time': now}))
            str = ''
            for i in data:
                if i['name'] == 'show interface status':
                    str+=self.show_interface_status(i)
                if i['name'] == 'show ip interface':
                    str+=self.show_ip_interface(i)
                if i['name'] == 'show vlan summary':
                    str+=self.show_vlan_summary(i)
                print(i['name'])
            results.ids.result.text = str

        else:
            pass
    def show_interface_status(self, i):
        content=i['contents']
        list=content.split('\n')
        up=0
        down=0
        for item in list:
            x=re.search('up', item)
            y=re.search('down', item)
            if x is None and y is None:
                continue
            elif x is None:
                down=down+1
            elif y is None:
                up=up+1
            elif x.span()[1]<y.span()[1]:
                up=up+1
            else:
                down=down+1
        string='[color=0000FF][b][size=30sp]Show Interface Status[/color][/b][/size]'
        string+='\n\n\n'
        string+='Number of UP Interfaces : '
        string+= str(up)
        string+='\n'
        string+='Number of DOWN Interfaces :'
        string+= str(down)
        string += '\n\n\n'
        string+=i['contents']
        string += '\n\n\n'
        return string

    def show_ip_interface(self, i):
        content = i['contents']
        list = content.split('\n')
        up = 0
        down = 0
        for item in list:
            x = re.search('(?s:.*)up', item)
            y = re.search('(?s:.*)down', item)
            if x is None and y is None:
                continue
            elif x is None:
                down = down + 1
            elif y is None:
                up = up + 1
            elif x.span()[1] > y.span()[1]:
                up = up + 1
            else:
                down = down + 1
        string = '[color=0000FF][b][size=30sp]Show IP Interface[/color][/b][/size]'
        string += '\n\n\n'
        string += 'Number of UP Interfaces : '
        string += str(up)
        string += '\n'
        string += 'Number of DOWN Interfaces :'
        string += str(down)
        string += '\n\n\n'
        string += i['contents']
        string += '\n\n\n'
        return string


    def show_vlan_summary(self, i):
        content = i['contents']
        list = content.split('\n')
        count = 0
        for item in list:
            x = re.search('enabled', item)
            y = re.search('disabled', item)
            if x is None and y is None:
                continue
            else:
                count = count + 1
        string = '[color=0000FF][b][size=30sp]Show Vlan Summary[/color][/b][/size]'
        string += '\n\n\n'
        string += 'Number of entries : '
        string += str(count)
        string += '\n\n\n'
        string += i['contents']
        string += '\n\n\n'
        return string


# ---------------------------------------------------------------------------------------------------------------

# project.kv ,where all the designing part has been implemented
kv = Builder.load_file('project.kv')


class ProjectApp(App):
    def build(self):
        return kv


# -----------------------------------------------------------------------------------------------------------------


# Here we are calling the ProjectApp().run() function
if __name__ == '__main__':
    ProjectApp().run()
