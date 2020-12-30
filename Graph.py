#! /usr/bin/python3

"""
This file contains GUI code for Configuring of SBS Servo
Developed by - SB Components
http://sb-components.co.uk
"""

from read_pms import AirReader
# from servo_instruction import SBSServo
import logging

import threading
import os
import webbrowser
from tkinter import font
import tkinter as tk
from tkinter import messagebox
from serial.tools import list_ports
from time import sleep

# imports for Plotting
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import tkinter as ttk


class MainApp(tk.Tk):
    """
    This is a class for Creating Frames and Buttons for left and top frame
    """
    def __init__(self, *args, **kwargs):
        global logo, img, xy_pos

        tk.Tk.__init__(self, *args, **kwargs)

        self.screen_width = tk.Tk.winfo_screenwidth(self)
        self.screen_height = tk.Tk.winfo_screenheight(self)
        self.app_width = 800
        self.app_height = 480
        self.xpos = (self.screen_width / 2) - (self.app_width / 2)
        self.ypos = (self.screen_height / 2) - (self.app_height / 2)
        xy_pos = self.xpos, self.ypos
        self.port = "ttyS0"
        self.current_baud = 115200
        self.geometry(
            "%dx%d+%d+%d" % (self.app_width, self.app_height, self.xpos,
                             self.ypos))
        self.title(" SB Serial Servo Configuration")

        self.config(bg="gray85")

        img = tk.PhotoImage(file=path + '/Images/settings.png')
        logo = tk.PhotoImage(file=path + '/Images/sblogo.png')

        # self.top_frame = tk.Frame(self, height=int(self.app_height / 15), bd=2,
        #                           width=self.app_width, bg="gray85")
        # self.top_frame.pack(padx=(225, 0), side="top", fill="both")
        # self.top_frame.pack_propagate(0)
        #
        # self.left_frame = tk.Frame(self, width=int(self.app_width / 4),
        #                            bg="gray85")
        # self.left_frame.pack(side="left", fill="both")
        # self.left_frame.pack_propagate(0)

        self.right_frame = tk.Frame(self, bg="gray85")
        self.right_frame.pack(side="left", fill="both", expand=True)

        self.label_font = font.Font(family="Helvetica", size=10)
        self.heading_font = font.Font(family="Helvetica", size=12)

        # self.topframe_contents()

        # self.frames = {}

        # for F in (OperateFrame, ParameterFrame, GraphFrame, AboutFrame):
        #     frame_name = F.__name__
        frame = GraphFrame(parent=self.right_frame, controller=self)
        # self.frames[frame_name] = frame
        frame.config(bg="white")
        frame.grid(row=0, column=0, sticky="nsew")

        frame.tkraise()

        ports = list(list_ports.comports())
        for p in ports:
            if "USB2.0-Serial" in p:
                self.port = ((p.device).split("/"))[2]

        # self.leftframe_contents()
        # self.show_frame("OperateFrame")

    def operateButton(self):
        """
        This function raise and sunk Operate button on top frame
        """
        self.operate_button.config(relief="sunken", fg="SteelBlue2")
        self.graph_button.config(relief="raised", fg="black")
        self.about_button.config(relief="raised", fg="black")
        self.param_button.config(relief="raised", fg="black")
        self.show_frame("OperateFrame")

    def parameterButton(self):
        """
        This function raise and sunk Parameter button on top frame
        """
        self.operate_button.config(relief="raised", fg="black")
        self.about_button.config(relief="raised", fg="black")
        self.graph_button.config(relief="raised", fg="black")
        self.param_button.config(relief="sunken", fg="turquoise4")
        retFrame = self.get_frame("OperateFrame")
        if retFrame.readFlag:
            retFrame.servoContinousRead()
        self.show_frame("ParameterFrame")

    def aboutButton(self):
        """
        This function raise and sunk About Us button on top frame
        """
        self.operate_button.config(relief="raised", fg="black")
        self.param_button.config(relief="raised", fg="black")
        self.graph_button.config(relief="raised", fg="black")
        self.about_button.config(relief="sunken", fg="SteelBlue2")
        self.show_frame("AboutFrame")

    def graphButton(self):
        """
        This function raise and sunk About Us button on top frame
        """
        self.operate_button.config(relief="raised", fg="black")
        self.param_button.config(relief="raised", fg="black")
        self.graph_button.config(relief="sunken", fg="black")
        self.about_button.config(relief="raised", fg="SteelBlue2")
        self.show_frame("GraphFrame")

    def connectPort(self):
        """
        This function connects the serial port
        """
        if self.connect_button.cget('text') == 'Connect' and \
                self.com_entry.get():
            # robot.connect("/dev/" + self.com_entry.get(),
            #               self.select_baud.get())

            robot.connect(self.com_entry.get(),
                          self.select_baud.get())
            if robot.alive:
                self.connect_button.config(relief="sunken", text="Disconnect")
                self.circle.itemconfigure(self.indication, fill="green3")
                self.com_entry.config(state="readonly")
                self.baud_opt.config(state="disable")
                self.current_baud = self.select_baud.get()

        elif self.connect_button.cget('text') == 'Disconnect':
            retFrame = self.get_frame("OperateFrame")
            if retFrame.readFlag:
                messagebox.showinfo("Thread Error", "Stop Continuous Read..!!")
            else:
                self.connect_button.config(relief="raised", text="Connect")
                self.circle.itemconfigure(self.indication, fill="red")
                robot.disconnect()
                self.com_entry.config(state="normal")
                self.baud_opt.config(state="normal")
        else:
            errorLabel = tk.Label(self.left_frame, text="Enter Comm Port..!!",
                                  bg="yellow")
            errorLabel.grid(row=4, column=0)
            errorLabel.after(2000, errorLabel.grid_forget)


class GraphFrame(tk.Frame):
    """
    This is a class for Creating widgets for Matplotlib Graph
    """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.readFlag = False

        #  Graph Variables
        self.xList = [i for i in range(50)]
        self.pm_1_list = [0] * 50
        self.pm_10_list = [0] * 50
        self.pm_25_list = [0] * 50
        self.CurrentList = [0] * 50


        self.LARGE_FONT = ("Verdana", 12)
        style.use("ggplot")

        #  Checkbox Variables
        self.PositionCheck = tk.IntVar()
        self.TorqueCheck = tk.IntVar()
        self.SpeedCheck = tk.IntVar()
        self.PositionCheck.set(1)
        self.TorqueCheck.set(1)
        self.SpeedCheck.set(1)

        chk = tk.Checkbutton(self, text="Position", fg='green',
                             variable=self.PositionCheck).grid(row=1,
                                                               column=0,
                                                               pady=10)
        chk = tk.Checkbutton(self, text="Torque", fg='red',
                             variable=self.TorqueCheck).grid(row=1,
                                                             column=1, pady=10)
        chk = tk.Checkbutton(self, text="Speed", fg='blue',
                             variable=self.SpeedCheck).grid(row=1, column=2,
                                                            pady=10)

        #  Start Button
        self.start_button = ttk.Button(self, text="Start", bg="gray90",
                                       width=6,
                                       command=self.servoContinousRead)
        self.start_button.grid(row=1, column=4)

        #  Servo Functions
        self.IDVar = tk.IntVar()
        self.IDVar.set(1)
        self.posVar = tk.IntVar()
        self.posVar.set(500)
        self.timeVar = tk.IntVar()
        self.timeVar.set(500)
        self.speedVar = tk.IntVar()
        self.speedVar.set(500)

        ent_vcmd = (self.register(self.ent_validate), '%P')
        id_vcmd = (self.register(self.id_validate), '%P')

        tk.Label(self, bg="white", fg="black", text="Servo ID").grid(row=3,
                                                                     column=0)
        tk.Entry(self, validate='key', validatecommand=id_vcmd, width=6,
                 textvariable=self.IDVar).grid(row=4, column=0)

        tk.Label(self, text="Time (ms)", bg="white", fg="black").grid(row=3,
                                                                      column=1)
        tk.Entry(self, validate='key', validatecommand=ent_vcmd, width=6,
                 textvariable=self.timeVar).grid(row=4, column=1)

        tk.Label(self, text="Speed (°/s)", bg="white", fg="black").grid(
            row=3, column=2)
        tk.Entry(self, validate='key', validatecommand=ent_vcmd, width=6,
                 textvariable=self.speedVar).grid(row=4, column=2)

        tk.Label(self, text="Position", bg="white", fg="black").grid(row=3,
                                                                     column=3)
        tk.Entry(self, validate='key', validatecommand=ent_vcmd, width=6,
                 textvariable=self.posVar).grid(row=4, column=3)

        # Write Button
        tk.Button(self, text="Write", bg="gray90", width=6,
                  command=self.writeParameters).grid(row=4, column=4)

        #  Graph Plotting
        self.ani = None

        self.fig = Figure(figsize=(8, 3.85), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=0, column=0, padx=0, pady=0,
                                         rowspan=1, sticky="en", columnspan=5)

    def animate(self, i):
        self.ax.clear()

        if self.PositionCheck.get():
            self.ax.plot(self.xList, self.pm_1_list, color='green')

        if self.TorqueCheck.get():
            self.ax.plot(self.xList, self.pm_10_list, color='red')

        if self.SpeedCheck.get():
            self.ax.plot(self.xList, self.pm_25_list, color='blue')

    def servoContinousRead(self):
        """
        This function create thread to read params from servo motor
        """
        if robot.alive:    
            if self.start_button.cget('text') == 'Start':
                # self.id_entry.config(state="readonly")
                self.readFlag = True
                self.threadContRead = threading.Thread(target=self.read_servo)
                self.threadContRead.daemon = True
                self.threadContRead.start()

                if self.ani:
                    self.ani.event_source.start()
                    self.start_button.config(relief="sunken", text='Stop')

                elif self.ani is None:
                    self.ani = animation.FuncAnimation(self.fig, self.animate,
                                                       interval=1,
                                                       repeat=False)
                    self.ani._start()
                    self.start_button.config(relief="sunken", text='Stop')

            elif self.start_button.cget('text') == 'Stop':
                # self.id_entry.config(state="normal")
                self.ani.event_source.stop()
                self.start_button.config(relief="raised", text='Start')

                self.readFlag = False

        else:
            messagebox.showerror("Comm Error",
                                 "Comm Port is not Connected..!!")

    def read_servo(self):
        while self.readFlag:
            try:   
                pm_1, pm_25, pm_10 = robot.update_data()
                print("Values {}".format(pm_1))
                self.pm_1_list.pop(0)
                self.pm_1_list.append(pm_1)
                self.pm_25_list.pop(0)
                self.pm_25_list.append(pm_25)
                self.pm_10_list.pop(0)
                self.pm_10_list.append(pm_10)

            except TypeError:
                self.servoContinousRead()
                messagebox.showerror("Response Error", "No Response from "
                                                       "Motor..!!")

    def writeParameters(self):
        """
        This function write all the parameters to servo motor
        """
        # try:
        #     if self.IDVar.get():
        #         if robot.alive:
        #             robot.servoWrite(int(self.IDVar.get()),
        #                              int(self.posVar.get()),
        #                              int(self.timeVar.get()),
        #                              int(self.speedVar.get()))
        #     else:
        #         messagebox.showerror("Comm Error",
        #                              "Comm Port is not Connected..!!")
        #
        # except ValueError as Ve:
        #     messagebox.showerror("Value Error", "Fill all fields!!")
        pass

    def ent_validate(self, new_value):
        """
        Validate the ID of servo in Operate frame
        """
        try:
            if not new_value or 0 < int(new_value) <= 253:
                return True
            else:
                self.bell()
                return False
        except ValueError:
            self.bell()
            return False

    def id_validate(self, new_value):
        """
        Validate the ID of servo in Operate frame
        """
        try:
            if not new_value or 0 < int(new_value) <= 253:
                return True
            else:
                self.bell()
                return False
        except ValueError:
            self.bell()
            return False


robot = None
logo = None
img = None
path = os.path.abspath(os.path.dirname(__file__))
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

if __name__ == "__main__":
    robot = AirReader()
    app = MainApp()
    app.tk.call('wm', 'iconphoto', app._w, img)
    app.resizable(0, 0)
    app.mainloop()
