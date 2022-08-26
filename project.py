# imported packages
from kivy.app import App
import datetime
from kivy.uix.label import Label
import tarfile
import os
import re
import threading
from kivy.properties import ObjectProperty
from kivy.uix.button import Button
from kivy.clock import Clock, mainthread
from kivy.core.text import LabelBase
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
import win32timezone

# ----------------------------------------------------------------------------------------------------------------
kivy.require('1.9.0')

kivy.config.Config.set('graphics', 'resizable', True)

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


class wrong_file_choosen(Screen):

    def ChangeFromResultsToMyLayout(self):
        kv.current = 'MyLayout'


class CustomLabel(Label):
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

    # Used to change the text from "no file chosen" to "file_name"
    def upload(self, filename, filepath):
        my_layout = self.manager.get_screen('MyLayout')
        try:
            my_layout.ids.file_choosen.text = filename[0]
        except:
            pass


# -----------------------------------------------------------------------------------------------------------------


# First Screen
class MyLayout(Screen):

    # -------------------------------- Used for text area ----------------------------------------------------------

    # function called when click on "analyse" button
    # def analyse_text(self):
    #     # text written is Empty
    #     if self.ids.text_input.text == '':
    #         self.ids.text_input.text = ''
    #     else:
    #         try:
    #             # creation of MongoClient
    #             client = MongoClient()
    #             # Connect with the port number and host
    #             client = MongoClient("mongodb://localhost:27017/")
    #             db = client["ShowTechAnalyser"]
    #             collection = db["Data"]
    #             now = datetime.datetime.now()
    #             # insert the data with time
    #             db.collection.insert_one({'contents': self.ids.text_input.text, 'time': now})
    #             self.ids.text_input.text = ''
    #             # changing screen from "MyLayout" to "Analyse"
    #             kv.current = 'Analyse'
    #             # clock time of 8 sec screen
    #             Clock.schedule_once(self.switch, 8)
    #             # result shown in "Results" Screen with the data fetch from database with the help of time
    #             results = self.manager.get_screen('Results')
    #             data = db.collection.find_one({'time': now})
    #             lst = data['contents'].split('\n')
    #             s = '\n'.join(lst)
    #             results.ids.result.text = '[b]' + s + '[/b]'
    #
    #         except:
    #             pass

    # use to reset text to empty
    # def reset_text(self):
    #     self.ids.text_input.text = ''

    # -----------------------------------------End for text area ---------------------------------------------

    # use to reset file to "no file chosen"
    def reset_file(self):
        self.ids.file_choosen.text = 'no file chosen'

    # called in line number 96
    def switch(self, *args):
        kv.current = "Results"

    # use to analyse file
    def extract_upload(self, *args):
        path = self.ids.file_choosen.text
        file = tarfile.open(path)
        file_name = file.getnames()

        dump_files = []
        for i in range(1, len(file_name) - 1):
            file_name_split = file_name[i].split('/')
            if file_name_split[1] == 'dump':
                dump_files.append(file_name[i])
        if len(dump_files) != 0:
            Clock.schedule_once(self.switch, 10)
            file.extractall('/sonic')
            now = datetime.datetime.now()
            file.close()
            insert = []
            for i in dump_files:
                f = open("/sonic" + '/' + i, 'r')
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

            self.ids.file_choosen.text = 'no file chosen'

            # changing the screen from "MyLayout" to "Analyse"

            results = self.manager.get_screen('Results')

            db.collection.insert_many(insert)

            # result shown in "Results" Screen with the data fetch from database with the help of time

            data = list(db.collection.find({'time': now}))
            str = ''
            # used to store the result of the analyzed commands so that they can be displayed with priority
            analyzed_commands = dict()
            for i in data:
                if i['name'] == 'show bridge vlan':
                    # calls show_bridge_vlan() function
                    analyzed_commands['show bridge vlan'] = self.show_bridge_vlan(i)

            for i in data:
                if i['name'] == 'show interface status':
                    # calls show_interface_status() function
                    analyzed_commands['show interface status'] = self.show_interface_status(i)
                elif i['name'] == 'show ip interface':
                    # calls show_ip_interface() function
                    analyzed_commands['show ip interface'] = self.show_ip_interface(i)
                elif i['name'] == 'show vlan summary':
                    # calls show_vlan_summary() function
                    if 'show bridge vlan' in analyzed_commands:
                        analyzed_commands['show vlan summary'] = self.show_vlan_summary(i, analyzed_commands[
                            'show bridge vlan'][1])
                    else:
                        analyzed_commands['show vlan summary'] = self.show_vlan_summary(i, [])
                elif i['name'] == 'show bridge fdb':
                    # calls show_bridge_fdb() function
                    analyzed_commands['show bridge fdb'] = self.show_bridge_fdb(i)
                elif i['name'] == 'show ip route':
                    # calls show_ip_route() function
                    analyzed_commands['show ip route'] = self.show_ip_route(i)
                elif i['name'] == 'show bgp summary':
                    # calls show_bgp_summary() function
                    analyzed_commands['show bgp summary'] = self.show_bgp_summary(i)
                elif i['name'] == 'show ip neigh':
                    # calls show_ip_neigh() function
                    analyzed_commands['show ip neigh'] = self.show_ip_neigh(i)
                elif i['name'] == 'show platform summary':
                    # calls show_platform_summary() function
                    analyzed_commands['show platform summary'] = self.show_platform_summary(i)
                elif i['name'] == 'show mirror summary':
                    # calls show_mirror_summary function
                    analyzed_commands['show mirror summary'] = self.show_mirror_summary(i)
                elif i['name'] == 'show port summary':
                    # calls show_port_summary() function
                    analyzed_commands['show port summary'] = self.show_port_summary(i)
                elif i['name'] == 'show lldpctl':
                    # calls show_lldpctl() function
                    analyzed_commands['show lldpctl'] = self.show_lldpctl(i)
                elif i['name'] == 'show top':
                    # calls show_top() function
                    analyzed_commands['show top'] = self.show_top(i)
                elif i['name'] == 'show version':
                    # calls show_version() function
                    analyzed_commands['show version'] = self.show_version(i)
                elif i['name'] == 'show broadcom knet link':
                    # calls show_broadcom_knet_link() function
                    analyzed_commands['show broadcom knet link'] = self.show_broadcom_knet_link(i)
                # elif i['name'] == 'show fp summary':
                #     # calls show_fp_summary() function
                #     analyzed_commands['show fp summary'] = self.show_fp_summary(i)
                elif i['name'] == 'show frr interfaces':
                    # calls show_frr_interfaces() function
                    analyzed_commands['show frr interfaces'] = self.show_frr_interfaces(i)
                elif i['name'] == 'show broadcom ps':
                    # calls show_broadcom_ps() function
                    analyzed_commands['show broadcom ps'] = self.show_broadcom_ps(i)
                print(i['name'])
            # arranging the commands according to priority
            str = ''
            if 'show platform summary' in analyzed_commands:
                str += analyzed_commands['show platform summary']
                del analyzed_commands['show platform summary']
            if 'show broadcom ps' in analyzed_commands:
                str += analyzed_commands['show broadcom ps']
                del analyzed_commands['show broadcom ps']
            if 'show broadcom knet link' in analyzed_commands and 'show interface status' in analyzed_commands:
                if analyzed_commands['show broadcom knet link'][1][0] == analyzed_commands['show interface status'][1][0] and analyzed_commands['show broadcom knet link'][1][1] == analyzed_commands['show interface status'][1][1] and analyzed_commands['show broadcom knet link'][1][2] == analyzed_commands['show interface status'][1][2]:
                    str+= '[color=#000000][size=20sp]' + 'NOTE: show broadcom knet link and show interface status ASIC and CLI command are matching\n\n' +'[/size][/color]'
                else:
                    str+= '[color=#000000][size=20sp]' + 'NOTE: show broadcom knet link and show interface status ASIC and CLI command are not matching\n\n' + '[/size][/color]'
            if 'show broadcom knet link' in analyzed_commands:
                str += analyzed_commands['show broadcom knet link'][0]
                del analyzed_commands['show broadcom knet link']
            if 'show interface status' in analyzed_commands:
                str += analyzed_commands['show interface status'][0]
                del analyzed_commands['show interface status']
            if 'show frr interfaces' in analyzed_commands:
                str += analyzed_commands['show frr interfaces']
                del analyzed_commands['show frr interfaces']
            if 'show fp summary' in analyzed_commands:
                str += analyzed_commands['show fp summary']
                del analyzed_commands['show fp summary']
            if 'show version' in analyzed_commands:
                str += analyzed_commands['show version']
                del analyzed_commands['show version']
            if 'show bridge vlan' in analyzed_commands:
                str += analyzed_commands['show bridge vlan'][0]
                del analyzed_commands['show bridge vlan']
            if 'show vlan summary' in analyzed_commands:
                str += analyzed_commands['show vlan summary']
                del analyzed_commands['show vlan summary']
            if 'show top' in analyzed_commands:
                str += analyzed_commands['show top']
                del analyzed_commands['show top']
            if 'show lldpctl' in analyzed_commands:
                str += analyzed_commands['show lldpctl']
                del analyzed_commands['show lldpctl']
            if 'show bgp summary' in analyzed_commands:
                str += analyzed_commands['show bgp summary']
                del analyzed_commands['show bgp summary']
            if 'show mirror summary' in analyzed_commands:
                str += analyzed_commands['show mirror summary']
                del analyzed_commands['show mirror summary']
            if 'show port summary' in analyzed_commands:
                str += analyzed_commands['show port summary']
                del analyzed_commands['show port summary']

            for ii, jj in analyzed_commands.items():
                str += jj
            Show_tech = str.split('\n')
            result_string = ''
            for i in range(0, len(Show_tech)):
                if i % 500 == 0:
                    label = CustomLabel(text=result_string, markup=True, font_name="Anonymous Pro")
                    results.ids.sv_box.add_widget(label)
                    result_string = ''
                result_string += Show_tech[i] + '\n'
            label = CustomLabel(text=result_string, markup=True, font_name="Anonymous Pro")
            results.ids.sv_box.add_widget(label)

        else:
            # for some file other than SONiC
            results = self.manager.get_screen('wrong_file_choosen')
            result_string = 'Choose a correct file !!'
            results.ids.text.text = result_string
            self.manager.current = 'wrong_file_choosen'

    def change_screen(self):
        # this will change screen to Analyse and again change to result screen after 10 seconds
        self.manager.current = 'Analyse'

    def analyse_file(self):
        # call change_screen() function and after one second cals extract_upload() function
        if self.ids.file_choosen.text != 'no file chosen':
            self.change_screen()
            Clock.schedule_once(self.extract_upload, 1)
        else:
            pass

    def show_broadcom_ps(self, i):
        content = i['contents']
        items = content.split('\n')
        up=0
        down=0
        result = ''
        for item in items:
            x = re.search('up ', item)
            y = re.search('down ', item)
            z = re.search('!ena ', item)
            if x is not None:
                up=up+1
                result += '[color=#014421]' + item + '[/color]' + '\n'
            elif y is not None or z is not None:
                down=down+1
                result+= '[color=#FF0000]'+ item+'[/color]'+'\n'
            else:
                result+= item+'\n'
        string = '[color=#0000FF][b][size=30sp]show broadcom ps[/color][/b][/size]'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Analysis..[/color][/b][/size]'
        string += '\n\n'
        string += '[color=#09075d][b]number of total links     :' + str(up+down) + '[/color][/b]'
        string += '\n'
        string += '[color=#014421]' + 'number of up links  :' + str(up) + '[/color]' + '\n'
        string += '[color=#FF0000]' + 'number of down links  :' + str(down) + '[/color]' + '\n'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Data..[/color][/b][/size]'
        string += '\n\n'
        string += result
        string += '\n\n\n'
        return string

    def show_frr_interfaces(self, i):
        content = i['contents']
        items = content.split('\n')
        count = 0
        result = ''
        for item in items:
            x = re.search('Interface', item)
            y = re.search('line protocol', item)
            if x is not None and y is not None:
                count = count + 1
                result += '[color=#014421]' + item + '[/color]' + '\n'
            else:
                result += item + '\n'

        string = '[color=#0000FF][b][size=30sp]show frr interfaces[/color][/b][/size]'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Analysis..[/color][/b][/size]'
        string += '\n\n'
        string += '[color=#09075d][b]number of total interfaces      :' + str(count) + '[/color][/b]'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Data..[/color][/b][/size]'
        string += '\n\n'
        string += result
        string += '\n\n\n'
        return string

    def show_fp_summary(self, i):
        content = i['contents']
        items = content.split('\n')
        count = 0
        result = ''
        for item in items:
            x = re.search('EID', item)

            if x is not None:
                count = count + 1
                result += '[color=#014421]' + item + '[/color]' + '\n'
            else:
                result += item + '\n'

        string = '[color=#0000FF][b][size=30sp]show fp summary[/color][/b][/size]'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Analysis..[/color][/b][/size]'
        string += '\n\n'
        string += '[color=#09075d][b]number of total EID \'s      :' + str(count) + '[/color][/b]'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Data..[/color][/b][/size]'
        string += '\n\n'
        string += result
        string += '\n\n\n'
        return string

    def show_broadcom_knet_link(self, i):
        content = i['contents']
        items = content.split('\n')
        down = 0
        up = 0
        result = ''
        for item in items:
            x = re.search('down', item)
            y = re.search('up', item)
            if x is not None:
                down = down + 1
                result += '[color=#FF0000]' + item + '[/color]' + '\n'
            elif y is not None:
                up = up + 1
                result += '[color=#014421]' + item + '[/color]' + '\n'
            else:
                result += item + '\n'

        string = '[color=#0000FF][b][size=30sp]show broadcom knet link[/color][/b][/size]'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Analysis..[/color][/b][/size]'
        string += '\n\n'
        string += '[color=#09075d][b]number of total interfaces      :' + str(up + down) + '[/color][/b]'
        string += '\n'
        string += '[color=#FF0000][b]number of total DOWN interfaces :' + str(down) + '[/color][/b]'
        string += '\n'
        string += '[color=#014421][b]number of total UP interfaces   :' + str(up) + '[/color][/b]'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Data..[/color][/b][/size]'
        string += '\n\n'
        string += result
        string += '\n\n\n'
        return [string, [up+down, up, down]]

    def show_bridge_vlan(self, i):
        content = i['contents']
        items = content.split('\n')
        result = ''
        lst = []
        for item in items:
            x = re.search('Bridge', item)
            if x is not None:
                result += '[color=#014421]' + item + '[/color]' + '\n'
                values = item.split()
                lst.append(values[1])
            else:
                result += item + '\n'

        string = '[color=#0000FF][b][size=30sp]show bridge vlan[/color][/b][/size]'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Analysis..[/color][/b][/size]'
        string += '\n\n'
        string += '[color=#014421]' + 'number of bridges: ' + str(len(lst)) + '\n' + '[/color]'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Data..[/color][/b][/size]'
        string += '\n\n'
        string += result
        string += '\n\n\n'

        return [string, lst]

    def show_version(self, i):
        content = i['contents']
        result = ''
        items = content.split('\n')
        for item in items:
            x = re.search('SONiC Software Version:', item)
            y = re.search('HwSKU:', item)
            z = re.search('ASIC:', item)
            if x is not None:
                lst = item.split(':')
                result += '[color=#014421]' + 'SONiC Software Version : ' + lst[1] + '[/color]' + '\n'
            if y is not None:
                lst = item.split(':')
                result += '[color=#014421]' + 'Platform               : ' + lst[1] + '[/color]' + '\n'
            if z is not None:
                lst = item.split(':')
                result += '[color=#014421]' + 'ASIC                   : ' + lst[1] + '[/color]' + '\n'

        string = '[color=#0000FF][b][size=30sp]show version[/color][/b][/size]'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Analysis..[/color][/b][/size]'
        string += '\n\n'
        string += result
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Data..[/color][/b][/size]'
        string += '\n\n'
        string += content
        string += '\n\n\n'
        return string

    def show_top(self, i):
        content = i['contents']
        result = ''
        items = content.split('\n')
        for item in items:
            x = re.search('Cpu', item)
            if x is not None:
                lst = item.split()
                result += '[color=#014421]' + 'Percentage CPU sys ' + lst[3] + '[/color]'

        string = '[color=#0000FF][b][size=30sp]show top[/color][/b][/size]'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Analysis..[/color][/b][/size]'
        string += '\n\n'
        string += result
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Data..[/color][/b][/size]'
        string += '\n\n'
        string += content
        string += '\n\n\n'
        return string

    def show_lldpctl(self, i):
        content = i['contents']
        items = content.split('\n')
        result = ''
        count = 0
        for item in items:
            x = re.match('Interface:', item)
            y = re.search('ChassisID:', item)
            z = re.search('MgmtIP:', item)
            if x is not None:
                count = count + 1
                result += '\n[color=#014421]' + item + '[/color]' + '\n'
            elif y is not None:
                result += '[color=#014421]' + item + '[/color]' + '\n'
            elif z is not None:
                result += '[color=#014421]' + item + '[/color]' + '\n'
        string = '[color=#0000FF][b][size=30sp]show lldp control[/color][/b][/size]'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Analysis..[/color][/b][/size]'
        string += '\n\n'
        string += '[color=#09075d]Total number of interfaces: ' + str(count) + '[/color]' + '\n'
        string += '[color=#014421]' + result + '[/color]'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Data..[/color][/b][/size]'
        string += '\n\n'
        string += content
        string += '\n\n\n'
        return string

    def show_port_summary(self, i):
        content = i['contents']
        result = ''
        items = content.split('\n')
        disable = 0
        enable = 0
        for item in items:
            x = re.search('Disabled', item)
            y = re.search('Enabled', item)
            if x is None and y is None:
                result += '[color=#FFFFFF]' + item + '[/color]\n'
            elif x is not None:
                result += '[color=#FF0000]' + item + '[/color]' + '\n\n'
                disable = disable + 1
            elif y is not None:
                result += '[color=#014421]' + item + '[/color]' + '\n\n'
                enable = enable + 1

        string = '[color=#0000FF][b][size=30sp]show port summary[/color][/b][/size]'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Analysis..[/color][/b][/size]'
        string += '\n\n'

        string += '[color=#014421]Number of entries which are enabled       : [/color]'
        string += '[color=#014421]' + str(enable) + '[/color]'
        string += '\n'
        string += '[color=#FF0000]Number of entries which are disabled      : [/color]'
        string += '[color=#FF0000]' + str(disable) + '[/color]'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Data..[/color][/b][/size]'
        string += '\n\n'
        string += result
        string += '\n\n\n'
        return string

    def show_mirror_summary(self, i):
        content = i['contents']
        string = '[color=#0000FF][b][size=30sp]show mirror summary[/color][/b][/size]'
        string += '\n\n\n'
        string += '[color=#FFFFFF]' + content + '[/color]'
        string += '\n\n\n'
        return string

    def show_platform_summary(self, i):
        result = ''
        content = i['contents']
        items = content.split('\n')
        proper_spacing = dict()
        left_max_length = 0
        right_max_length = 0
        for item in items:
            lst = item.split(':')
            if len(lst) == 2:
                if left_max_length < len(lst[0]):
                    left_max_length = len(lst[0])
                if right_max_length < len(lst[1]):
                    right_max_length = len(lst[1])
                proper_spacing[lst[0]] = lst[1]
        left_max_length += 2
        right_max_length += 2
        for ii, jj in proper_spacing.items():
            left = ii
            right = jj
            for spaces in range(len(ii), left_max_length + 1):
                left += ' '
            for spaces in range(len(jj), right_max_length + 1):
                right += ' '
            result += '[color=#014421]' + left.upper() + ':' + right + '[/color]' + '\n'
        string = '[color=0000FF][b][size=30sp]show platform summary[/color][/b][/size]'
        string += '\n\n\n'
        string += result
        string += '\n\n\n'
        return string

    def show_ip_neigh(self, i):

        result = ''
        content = i['contents']
        items = content.split('\n')
        permanent = 0
        noarp = 0
        reachable = 0
        stale = 0
        none = 0
        incomplete = 0
        delay = 0
        probe = 0
        failed = 0
        for item in items:
            a = re.search('PERMANENT', item)
            b = re.search('NOARP', item)
            c = re.search('REACHABLE', item)
            d = re.search('STALE', item)
            e = re.search('NONE', item)
            f = re.search('INCOMPLETE', item)
            g = re.search('DELAY', item)
            h = re.search('PROBE', item)
            ii = re.search('FAILED', item)
            if a is not None:
                result += '[color=#014421]' + item + '[/color]' + '\n'
                permanent = permanent + 1
            elif b is not None:
                result += '[color=#FF0000]' + item + '[/color]' + '\n'
                noarp = noarp + 1
            elif c is not None:
                result += '[color=#014421]' + item + '[/color]' + '\n'
                reachable = reachable + 1
            elif d is not None:
                result += '[color=#FF0000]' + item + '[/color]' + '\n'
                stale = stale + 1
            elif e is not None:
                result += '[color=#FF0000]' + item + '[/color]' + '\n'
                none = none + 1
            elif f is not None:
                result += '[color=#FF0000]' + item + '[/color]' + '\n'
                incomplete = incomplete + 1
            elif g is not None:
                result += '[color=#FF0000]' + item + '[/color]' + '\n'
                delay = delay + 1
            elif h is not None:
                result += '[color=#FF0000]' + item + '[/color]' + '\n'
                probe = probe + 1
            elif ii is not None:
                result += '[color=#FF0000]' + item + '[/color]' + '\n'
                failed = failed + 1
        # These all statements are used for formatting the results to show in result screen.
        string = '[color=0000FF][b][size=30sp]show ip neighbour[/color][/b][/size]'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Analysis..[/color][/b][/size]'
        string += '\n\n'
        string += '[color=#09075d]Number of entries                        : [/color]'
        string += '[color=#09075d]' + str(
            permanent + noarp + reachable + stale + none + incomplete + delay + probe + failed) + '[/color]'
        string += '\n'
        string += '[color=#014421]Number of entries with status PERMANENT  : [/color]'
        string += '[color=#014421]' + str(permanent) + '[/color]'
        string += '\n'
        string += '[color=#FF0000]Number of entries with status NOARP      : [/color]'
        string += '[color=#FF0000]' + str(noarp) + '[/color]'
        string += '\n'
        string += '[color=#014421]Number of entries with status REACHABLE  : [/color]'
        string += '[color=#014421]' + str(reachable) + '[/color]'
        string += '\n'
        string += '[color=#FF0000]Number of entries with status STALE      : [/color]'
        string += '[color=#FF0000]' + str(stale) + '[/color]'
        string += '\n'
        string += '[color=#FF0000]Number of entries with status NONE       : [/color]'
        string += '[color=#FF0000]' + str(none) + '[/color]'
        string += '\n'
        string += '[color=#FF0000]Number of entries with status INCOMPLETE : [/color]'
        string += '[color=#FF0000]' + str(incomplete) + '[/color]'
        string += '\n'
        string += '[color=#FF0000]Number of entries with status DELAY      : [/color]'
        string += '[color=#FF0000]' + str(delay) + '[/color]'
        string += '\n'
        string += '[color=#FF0000]Number of entries with status PROBE      : [/color]'
        string += '[color=#FF0000]' + str(probe) + '[/color]'
        string += '\n'
        string += '[color=#FF0000]Number of entries with status FAILED     : [/color]'
        string += '[color=#FF0000]' + str(failed) + '[/color]'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Data..[/color][/b][/size]'
        string += '\n\n'
        string += result
        string += '\n\n\n'
        return string

    def show_bgp_summary(self, i):
        content = i['contents']
        result = ''
        ans = ''
        AS = dict()
        items = content.split('\n')
        for item in items:
            x = re.match('([01]?\d\d?|2[0-4]\d|25[0-5])(\.[01]?\d\d?|\.2[0-4]\d|\.25[0-5]){3}', item)
            y = re.match('Neighbor', item)
            z = re.match('Total number of neighbors', item)

            establish = re.search('Established', item)

            if x is not None:
                lst = item.split()
                AS[lst[2]] = AS.get(lst[2], 0) + 1
                if establish is not None:
                    result += '[color=#014421]' + item + '[/color]' + '\n'
                else:
                    result += '[color=#FF0000]' + item + '[/color]' + '\n'
            elif y is not None:
                result += '[color=#000000]' + item + '[/color]' + '\n'
            elif z is not None:
                ans += '[color=#09075d]' + item + '[/color]' + '\n\n'

        string = '[color=0000FF][b][size=30sp]show bgp summary[/color][/b][/size]'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Analysis..[/color][/b][/size]'
        string += '\n\n'
        string += ans
        string += '\n'
        string += '[color=#014421]Total number of AS ' + str(len(AS)) + '\n'
        for i, j in AS.items():
            string += '[color=#014421]number of entries with AS ' + i + ' ' + str(j) + '\n'
        string += '\n\n'
        string += '[color=000000][b][size=20sp]Data..[/color][/b][/size]'
        string += '\n\n'
        string += result
        string += '\n\n\n'
        return string

    # This function match the statement which starts from IP address e.g, 10.0.0.1/32
    def show_ip_route(self, i):
        content = i['contents']
        list = content.split('\n')
        count = 0
        result = ''
        linkdown = 0
        for item in list:
            # regex match the statement starts with an IP address
            x = re.match('([01]?\d\d?|2[0-4]\d|25[0-5])(\.[01]?\d\d?|\.2[0-4]\d|\.25[0-5]){3}(/[0-2]\d|/3[0-2])', item)
            if x is None:
                result += item + '\n'
            else:
                # regex search the statement which contains linkdown
                y = re.search('linkdown', item)
                if y is not None:
                    result += '[color=#FF0000]' + item + '[/color]' + '\n'
                    linkdown = linkdown + 1
                else:
                    result += '[color=#014421]' + item + '[/color]' + '\n'
                count = count + 1
        # These all statements are used for formatting the results to show in result screen.
        string = '[color=0000FF][b][size=30sp]show ip route[/color][/b][/size]'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Analysis..[/color][/b][/size]'
        string += '\n\n'
        string += '[color=#09075d]Number of entries                  : [/color]'
        string += '[color=#09075d]' + str(count) + '[/color]'
        string += '\n'
        string += '[color=#FF0000]Number of entries with linkdown    : [/color]'
        string += '[color=#FF0000]' + str(linkdown) + '[/color]'
        string += '\n'
        string += '[color=#014421]Number of entries without linkdown : [/color]'
        string += '[color=#014421]' + str(count - linkdown) + '[/color]'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Data..[/color][/b][/size]'
        string += '\n\n'
        string += result
        string += '\n\n\n'
        return string

    # This function match the statement which starts from mac-address e.g, 01:01:01:01:01:01
    def show_bridge_fdb(self, i):
        content = i['contents']
        interface = dict()
        list = content.split('\n')
        count = 0
        for item in list:
            # regex match the statement starts with a mac-address
            value = item.split()
            x = re.match('(?:[0-9a-fA-F]:?){12}', item)
            if x is None:
                continue
            else:
                interface[value[2]] = interface.get(value[2], 0) + 1
                count = count + 1
        # These all statements are used for formatting the results to show in result screen.
        string = '[color=0000FF][b][size=30sp]show bridge fdb[/color][/b][/size]'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Analysis..[/color][/b][/size]'
        string += '\n\n'
        string += '[color=#09075d]Number of entries                              : [/color]'
        string += '[color=#09075d]' + str(count) + '[/color]'
        string += '\n'
        for key, value in interface.items():
            ans = key
            for space in range(len(key), 15):
                ans += ' '
            string += '[color=#014421]Number of entries in interface ' + ans + ' : ' + str(value) + ' [/color]' + '\n'
        string += '\n\n'
        string += '[color=000000][b][size=20sp]Data..[/color][/b][/size]'
        string += '\n\n'
        string += i['contents']
        string += '\n\n\n'
        return string

    # This function searches for number of UP and DOWN Interfaces on teh basis of oper.
    def show_interface_status(self, i):
        content = i['contents']
        list = content.split('\n')
        result = ''
        up = 0
        down = 0
        for item in list:
            # regex for searching the statement which contains UP
            x = re.search('up', item)
            # regex for searching the statement which contains DOWN
            y = re.search('down', item)
            if x is None and y is None:
                result += '[color=#000000]' + item + '[/color]' + '\n'
            elif x is None:
                result += '[color=#FF0000]' + item + '[/color]' + '\n'
                down = down + 1
            elif y is None:
                result += '[color=#014421]' + item + '[/color]' + '\n'
                up = up + 1
            elif x.span()[1] < y.span()[1]:
                result += '[color=#014421]' + item + '[/color]' + '\n'
                up = up + 1
            else:
                result += '[color=#FF0000]' + item + '[/color]' + '\n'
                down = down + 1
        # These all statements are used for formatting the results to show in result screen.
        string = '[color=0000FF][b][size=30sp]show interface status[/color][/b][/size]'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Analysis..[/color][/b][/size]'
        string += '\n\n'
        string += '[color=#09075d]Total number of Interfaces : [/color]'
        string += '[color=#09075d]' + str(up + down) + '[/color]'
        string += '\n'
        string += '[color=#014421]Number of UP Interfaces    : [/color]'
        string += '[color=#014421]' + str(up) + '[/color]'
        string += '\n'
        string += '[color=#FF0000]Number of DOWN Interfaces  :[/color]'
        string += '[color=#FF0000]' + str(down) + '[/color]'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Data..[/color][/b][/size]'
        string += '\n\n'
        string += result
        string += '\n\n\n'
        return [string, [up+down, up, down]]

    # This function searches for number of UP and DOWN Interfaces on the basis of oper.
    def show_ip_interface(self, i):
        content = i['contents']
        list = content.split('\n')
        up = 0
        down = 0
        result = ''
        for item in list:
            # regex for searching the statement which contains UP
            x = re.search('(?s:.*)up', item)
            # regex for searching the statement which contains DOWN
            y = re.search('(?s:.*)down', item)
            if x is None and y is None:
                result += '[color=#000000]' + item + '[/color]' + '\n'
            elif x is None:
                result += '[color=#FF0000]' + item + '[/color]' + '\n'
                down = down + 1
            elif y is None:
                result += '[color=#014421]' + item + '[/color]' + '\n'
                up = up + 1
            elif x.span()[1] > y.span()[1]:
                result += '[color=#014421]' + item + '[/color]' + '\n'
                up = up + 1
            elif x.span()[1] < y.span()[1]:
                result += '[color=#FF0000]' + item + '[/color]' + '\n'
                down = down + 1
            else:
                result += item
        # These all statements are used for formatting the results to show in result screen.
        string = '[color=0000FF][b][size=30sp]show ip interface[/color][/b][/size]'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Analysis..[/color][/b][/size]'
        string += '\n\n'
        string += '[color=#09075d]Total number of Interfaces : [/color]'
        string += '[color=#09075d]' + str(up + down) + '[/color]'
        string += '\n'
        string += '[color=#014421]Number of UP Interfaces    : [/color]'
        string += '[color=#014421]' + str(up) + '[/color]'
        string += '\n'
        string += '[color=#FF0000]Number of DOWN Interfaces  : [/color]'
        string += '[color=#FF0000]' + str(down) + '[/color]'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Data..[/color][/b][/size]'
        string += '\n\n'
        string += result
        string += '\n\n\n'
        return string

    # This function searches for number of Vlan Entries.
    def show_vlan_summary(self, i, lst):
        content = i['contents']
        list = content.split('\n')
        result = ''
        count = 0
        for item in list:
            x = re.search('enabled', item)
            y = re.search('disabled', item)
            if x is None and y is None:
                result += '[color=#000000]' + item + '[/color]' + '\n'
            else:
                result += item + '\n'
                count = count + 1
        # These all statements are used for formatting the results to show in result screen.
        string = '[color=0000FF][b][size=30sp]show vlan summary[/color][/b][/size]'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Analysis..[/color][/b][/size]'
        string += '\n\n'
        string += '[color=#09075d]Number of entries : [/color]'
        string += '[color=#09075d]' + str(count) + '[/color]'
        string += '\n'
        string += '[color=#014421]available bridges from "show bridge vlan" command  :' + str(lst) + ' [/color]'
        string += '\n\n\n'
        string += '[color=000000][b][size=20sp]Data..[/color][/b][/size]'
        string += '\n\n'
        string += result
        string += '\n\n\n'
        return string


# ---------------------------------------------------------------------------------------------------------------

# project.kv ,where all the designing part has been implemented
kv = Builder.load_file('project.kv')


class ProjectApp(App):
    def build(self):
        return kv


# -----------------------------------------------------------------------------------------------------------------

LabelBase.register(name='Anonymous Pro', fn_regular='Anonymous_Pro.ttf')
# Here we are calling the ProjectApp().run() function
ProjectApp().run()
