import os
import time
import pickle
import threading
from tkinter import Tk, Entry, W, E, N, S, PhotoImage, Checkbutton, Button, \
        Menu, Frame, Label, Spinbox, END, BooleanVar, messagebox
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import pygame


PROGRAM_NAME = ' Explosion Drum Machine '
MAX_NUMBER_OF_PATTERNS = 10
MAX_NUMBER_OF_DRUM_SAMPLES = 5
MAX_NUMBER_OF_UNITS = 5
MAX_BPU = 5
INITIAL_NUMBER_OF_UNITS = 4
INITIAL_BPU = 4
INITIAL_BEATS_PER_MINUTE = 240
MIN_BEATS_PER_MINUTE = 80
MAX_BEATS_PER_MINUTE = 360
COLOR_1 = 'grey55'
COLOR_2 = 'khaki'
BUTTON_CLICKED_COLOR = 'green'


class DrumMachine:

    def __init__(self, root):
        self.root = root
        self.root.title(PROGRAM_NAME)
        self.all_patterns = [None] * MAX_NUMBER_OF_PATTERNS
        self.current_pattern_index = 0
        self.loop = True
        self.now_playing = False
        self.beats_per_minute = INITIAL_BEATS_PER_MINUTE
        self.drum_load_entry_widget = [None] * MAX_NUMBER_OF_DRUM_SAMPLES
        self.root.protocol('WM_DELETE_WINDOW', self.exit_app)
        self.init_all_patterns()
        self.init_gui()

    def get_current_pattern_dict(self):
        return self.all_patterns[self.current_pattern_index]

    def get_bpu(self):
        return self.get_current_pattern_dict()['bpu']

    def set_bpu(self):
        self.get_current_pattern_dict()['bpu'] = int(self.bpu_widget.get())

    def get_number_of_units(self):
        return self.get_current_pattern_dict()['number_of_units']

    def set_number_of_units(self):
        self.get_current_pattern_dict(
        )['number_of_units'] = int(self.number_of_units_widget.get())

    def get_list_of_drum_files(self):
        return self.get_current_pattern_dict()['list_of_drum_files']

    def get_drum_file_path(self, drum_index):
        return self.get_list_of_drum_files()[drum_index]

    def set_drum_file_path(self, drum_index, file_path):
        self.get_list_of_drum_files()[drum_index] = file_path

    def get_is_button_clicked_list(self):
        return self.get_current_pattern_dict()['is_button_clicked_list']

    def set_is_button_clicked_list(self, num_of_rows, num_of_columns):
        self.get_current_pattern_dict()['is_button_clicked_list'] = [
            [False] * num_of_columns for x in range(num_of_rows)]


    def set_beats_per_minute(self):
        self.get_current_pattern_dict(
        )['beats_per_minute'] = self.beats_per_minute_widget.get()

    def init_all_patterns(self):
        self.all_patterns = [
            {
                'list_of_drum_files': [None] * MAX_NUMBER_OF_DRUM_SAMPLES,
                'number_of_units': INITIAL_NUMBER_OF_UNITS,
                'bpu': INITIAL_BPU,
                'is_button_clicked_list':
                self.init_is_button_clicked_list(
                    MAX_NUMBER_OF_DRUM_SAMPLES,
                    INITIAL_NUMBER_OF_UNITS * INITIAL_BPU
                )
            }
            for k in range(MAX_NUMBER_OF_PATTERNS)]

    def init_is_button_clicked_list(self, num_of_rows, num_of_columns):
        return [[False] * num_of_columns for x in range(num_of_rows)]

    def load_project(self):
        file_path = filedialog.askopenfilename(
            filetypes=[('Explosion Beat File', '*.ebt')], title='Load Project')
        if not file_path:
            return
        pickled_file_object = open(file_path, "rb")
        try:
            self.all_patterns = pickle.load(pickled_file_object)
        except EOFError:
            messagebox.showerror("Error",
                                 "Explosion Beat file seems corrupted or invalid !")
        pickled_file_object.close()
        try:
            self.change_pattern()
            self.root.title(os.path.basename(file_path) + PROGRAM_NAME)
        except:
            messagebox.showerror("Error",
                                 "An unexpected error occurred trying to process the beat file")

    def save_project(self):
        saveas_file_name = filedialog.asksaveasfilename(
            filetypes=[('Explosion Beat File', '*.ebt')], title="Save project as...")
        if saveas_file_name is None:
            return
        pickle.dump(self.all_patterns, open(saveas_file_name, "wb"))
        self.root.title(os.path.basename(saveas_file_name) + PROGRAM_NAME)


    def show_about(self):
        messagebox.showinfo(PROGRAM_NAME,
                            "Tkinter GUI Application\n Development Blueprints")

    def exit_app(self):
        self.now_playing = False
        if messagebox.askokcancel("Quit", "Really quit?"):
            self.root.destroy()

    def display_pattern_name(self):
        self.current_pattern_name_widget.config(state='normal')
        self.current_pattern_name_widget.delete(0, 'end')
        self.current_pattern_name_widget.insert(0,
                                                'Pattern {}'.format(self.current_pattern_index))
        self.current_pattern_name_widget.config(state='readonly')

    def on_pattern_changed(self):
        self.change_pattern()

    def change_pattern(self):
        self.current_pattern_index = int(self.pattern_index_widget.get())
        self.display_pattern_name()
        self.create_left_drum_loader()
        self.display_all_drum_file_names()
        self.create_right_button_matrix()
        self.display_all_button_colors()

    def on_number_of_units_changed(self):
        self.set_number_of_units()
        self.set_is_button_clicked_list(MAX_NUMBER_OF_DRUM_SAMPLES,
                                        self.find_number_of_columns())
        self.create_right_button_matrix()

    def on_bpu_changed(self):
        self.set_bpu()
        self.set_is_button_clicked_list(MAX_NUMBER_OF_DRUM_SAMPLES,
                                        self.find_number_of_columns())
        self.create_right_button_matrix()

    def on_open_file_button_clicked(self, drum_index):
        def event_handler():
            file_path = filedialog.askopenfilename(defaultextension=".wav",
                                                   filetypes=[("Wave Files", "*.wav"), ("OGG Files", "*.ogg")])
            if not file_path:
                return
            self.set_drum_file_path(drum_index, file_path)
            self.display_all_drum_file_names()
        return event_handler

    def display_all_drum_file_names(self):
        for i, drum_name in enumerate(self.get_list_of_drum_files()):
            self.display_drum_name(i, drum_name)

    def display_drum_name(self, text_widget_num, file_path):
        if file_path is None:
            return
        drum_name = os.path.basename(file_path)
        self.drum_load_entry_widget[text_widget_num].delete(0, END)
        self.drum_load_entry_widget[text_widget_num].insert(0, drum_name)

    def play_in_thread(self):
        self.thread = threading.Thread(target = self.play_pattern)
        self.thread.start()

    def on_play_button_clicked(self):
        self.start_play()
        self.toggle_play_button_state()

    def start_play(self):
        self.init_pygame()
        self.play_in_thread()

    def on_stop_button_clicked(self):
        self.stop_play()
        self.toggle_play_button_state()

    def stop_play(self):
        self.now_playing = False


    def init_pygame(self):
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()

    def play_sound(self, sound_filename):
        if sound_filename is not None:
            pygame.mixer.Sound(sound_filename).play()

    def get_column_from_matrix(self, matrix, i):
        return [row[i] for row in matrix]

    def toggle_play_button_state(self):
        if self.now_playing:
            self.play_button.config(state="disabled")
        else:
            self.play_button.config(state="normal")

    def play_pattern(self):
        self.now_playing = True
        self.toggle_play_button_state()
        while self.now_playing:
            play_list = self.get_is_button_clicked_list()
            num_columns = len(play_list[0])
            for column_index in range(num_columns):
                column_to_play = self.get_column_from_matrix(
                      play_list, column_index)
                for i, item in enumerate(column_to_play):
                    if item:
                        sound_filename = self.get_drum_file_path(i)
                        self.play_sound(sound_filename)
                time.sleep(self.time_to_play_each_column())
                if not self.now_playing: break
            if not self.loop: break
        self.now_playing = False
        self.toggle_play_button_state()

    def time_to_play_each_column(self):
        beats_per_second = self.beats_per_minute / 60
        time_to_play_each_column = 1 / beats_per_second
        return time_to_play_each_column

    def on_loop_button_toggled(self):
        self.loop = self.loopbutton.instate(['selected'])

    def on_beats_per_minute_changed(self):
        self.beats_per_minute = int(self.beats_per_minute_widget.get())

    def get_button_value(self, row, col):
        return self.all_patterns[self.current_pattern_index][
            'is_button_clicked_list'][row][col]

    def find_number_of_columns(self):
        return int(self.number_of_units_widget.get()) * int(self.bpu_widget.get())

    def process_button_clicked(self, row, col):
        self.set_button_value(row, col, not self.get_button_value(row, col))
        self.display_button_color(row, col)

    def set_button_value(self, row, col, bool_value):
        self.all_patterns[self.current_pattern_index][
            'is_button_clicked_list'][row][col] = bool_value

    def on_button_clicked(self, row, col):
        def event_handler():
            self.process_button_clicked(row, col)
        return event_handler

    def display_all_button_colors(self):
        number_of_columns = self.find_number_of_columns()
        for r in range(MAX_NUMBER_OF_DRUM_SAMPLES):
            for c in range(number_of_columns):
                self.display_button_color(r, c)

    def display_button_color(self, row, col):
        bpu = int(self.bpu_widget.get())
        original_color = COLOR_1 if ((col//bpu) % 2) else COLOR_2
        button_color = BUTTON_CLICKED_COLOR if self.get_button_value(
            row, col) else original_color
        self.buttons[row][col].config(background=button_color)

    def create_play_bar(self):
        playbar_frame = Frame(self.root, height=15)
        start_row = MAX_NUMBER_OF_DRUM_SAMPLES + 10
        playbar_frame.grid(row=start_row, columnspan=13,
                           sticky=W + E, padx=15, pady=10)
        self.play_icon = PhotoImage(file="images/play.gif")
        self.play_button = ttk.Button(
            playbar_frame, text='Play',  image=self.play_icon, compound='left', command=self.on_play_button_clicked)
        self.play_button.grid(row=start_row, column=1, padx=2)
        ttk.Button(playbar_frame, text='Stop', command=self.on_stop_button_clicked).grid(
            row=start_row, column=3, padx=2)
        ttk.Separator(playbar_frame, orient='vertical').grid(
            row=start_row, column=5, sticky="ns", padx=5)
        self.loopbutton = ttk.Checkbutton(
            playbar_frame, text='Loop', command=self.on_loop_button_toggled)
        self.loopbutton.grid(row=start_row, column=16, padx=5)
        self.loopbutton.state(['selected'])
        ttk.Separator(playbar_frame, orient='vertical').grid(
            row=start_row, column=20, sticky="ns", padx=5)
        Label(playbar_frame, text='Beats Per Minute').grid(
            row=start_row, column=25)
        self.beats_per_minute_widget = Spinbox(playbar_frame, from_=MIN_BEATS_PER_MINUTE, to=MAX_BEATS_PER_MINUTE, width=5,
                increment=5.0, command=self.on_beats_per_minute_changed)
        self.beats_per_minute_widget.grid(row=start_row, column=30)
        self.beats_per_minute_widget.delete(0,"end")
        self.beats_per_minute_widget.insert(0,INITIAL_BEATS_PER_MINUTE)
        ttk.Separator(playbar_frame, orient='vertical').grid(
            row=start_row, column=35, sticky="ns", padx=5)
        photo = PhotoImage(file='images/signature.gif')
        label = Label(playbar_frame, image=photo)
        label.image = photo
        label.grid(row=start_row, column=50, padx=1, sticky='w')

    def create_right_button_matrix(self):
        right_frame = Frame(self.root)
        right_frame.grid(row=10, column=6, sticky=W +
                         E + N + S, padx=15, pady=4)
        self.buttons = [[None for x in range(
            self.find_number_of_columns())] for x in range(MAX_NUMBER_OF_DRUM_SAMPLES)]
        for row in range(MAX_NUMBER_OF_DRUM_SAMPLES):
            for col in range(self.find_number_of_columns()):
                self.buttons[row][col] = Button(
                    right_frame, command=self.on_button_clicked(row, col))
                self.buttons[row][col].grid(row=row, column=col)
                self.display_button_color(row, col)

    def create_left_drum_loader(self):
        left_frame = Frame(self.root)
        left_frame.grid(row=10, column=0, columnspan=6, sticky=W + E + N + S)
        open_file_icon = PhotoImage(file='images/openfile.gif')
        for i in range(MAX_NUMBER_OF_DRUM_SAMPLES):
            open_file_button = Button(left_frame, image=open_file_icon,
                                      command=self.on_open_file_button_clicked(i))
            open_file_button.image = open_file_icon
            open_file_button.grid(row=i, column=0,  padx=5, pady=4)
            self.drum_load_entry_widget[i] = Entry(left_frame)
            self.drum_load_entry_widget[i].grid(
                row=i, column=4, padx=7, pady=4)

    def create_top_bar(self):
        topbar_frame = Frame(self.root, height=25)
        topbar_frame.grid(row=0, columnspan=12, rowspan=10, padx=5, pady=5)

        Label(topbar_frame, text='Pattern Number:').grid(row=0, column=1)
        self.pattern_index_widget = Spinbox(topbar_frame, from_=0, to=MAX_NUMBER_OF_PATTERNS - 1, width=5,
                command=self.on_pattern_changed)
        self.pattern_index_widget.grid(row=0, column=2)
        self.current_pattern_name_widget = Entry(topbar_frame)
        self.current_pattern_name_widget.grid(row=0, column=3, padx=7, pady=2)

        Label(topbar_frame, text='Number of Units:').grid(row=0, column=4)
        self.number_of_units_widget = Spinbox(topbar_frame, from_=1, to=MAX_NUMBER_OF_UNITS, width=5,
                command=self.on_number_of_units_changed)
        self.number_of_units_widget.delete(0,"end")
        self.number_of_units_widget.insert(0,INITIAL_NUMBER_OF_UNITS)
        self.number_of_units_widget.grid(row=0, column=5)
        Label(topbar_frame, text='BPUs:').grid(row=0, column=6)
        self.bpu_widget = Spinbox(topbar_frame, from_=1, to=MAX_BPU, width=5,
                command=self.on_bpu_changed)
        self.bpu_widget.grid(row=0, column=7)
        self.bpu_widget.delete(0,"end")
        self.bpu_widget.insert(0,INITIAL_BPU)
        self.display_pattern_name()

    def create_top_menu(self):
        self.menu_bar = Menu(self.root)
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(
            label="Load Project", command=self.load_project)
        self.file_menu.add_command(
            label="Save Project", command=self.save_project)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.exit_app)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.about_menu = Menu(self.menu_bar, tearoff=0)
        self.about_menu.add_command(label="About", command=self.show_about)
        self.menu_bar.add_cascade(label="About", menu=self.about_menu)
        self.root.config(menu=self.menu_bar)

    def init_gui(self):
        self.create_top_menu()
        self.create_top_bar()
        self.create_left_drum_loader()
        self.create_right_button_matrix()
        self.create_play_bar()


if __name__ == '__main__':
    root = Tk()
    DrumMachine(root)
    root.mainloop()