import datetime
from functools import partial
from threading import Thread
from tkinter import *
from tkinter import ttk, messagebox
import time
import jsonpickle
import math
import geocoder
from PIL import Image, ImageTk


class Report:
    waiting_time = -1
    price_per_litre = -1

    def __init__(self, waiting_time, price_per_litre):
        self.waiting_time = convert_string_to_time(waiting_time)
        self.price_per_litre = price_per_litre


class GasStation:
    name = "Name"
    opening_hours = "Opening Hours"
    gas_remaining = "NONE"
    price_per_litre = -1
    location = (0, 0)
    time_data_points = {}

    def __init__(self, name, opening_hours, gas_remaining, price_per_litre, location,
                 time_data_points):
        self.name = name
        self.opening_hours = opening_hours
        self.gas_remaining = gas_remaining
        self.price_per_litre = price_per_litre
        self.location = location
        self.time_data_points = time_data_points

    def get_is_open(self):
        current_time = time.ctime(time.time()).split(" ")
        time_string = current_time[3]
        time_string_components = time_string.split(":")
        opening_hours_components = self.opening_hours.split(" ")
        current_hour = int(time_string_components[0])
        opening_hour = int(opening_hours_components[1])
        closing_hour = int(opening_hours_components[3])
        if opening_hour <= current_hour < closing_hour:
            return "Yes"
        else:
            return "No"

    def toString(self):
        return "Name: " + self.name + "\n" + "Opening Hours: " + self.opening_hours + "\n" + "Gas Remaining: " + self.gas_remaining \
               + "\n" + "Price per Litre: " + str(self.price_per_litre)


def save_gas_stations_to_file():
    gas_stations_file = open("gas_stations.txt", mode="w", encoding="utf-8")
    gas_stations_file.write(jsonpickle.encode(gas_stations))
    gas_stations_file.close()
    gas_stations_window.destroy()


def add_data_point(gas_station, waiting_time_entry, price_per_litre_entry, report_window):
    waiting_time = waiting_time_entry.get()
    price_per_litre = price_per_litre_entry.get()

    if len(waiting_time) == 0:
        messagebox.showerror("Empty Input", "You didn't tell us how much you waited!")
    elif len(price_per_litre) == 0:
        messagebox.showerror("Empty Input", "You didn't tell us the price per Litre!")
    else:
        temp_report = Report(waiting_time, price_per_litre)
        temp_data_points = gas_station.time_data_points
        current_time = get_current_time()
        temp_list = temp_data_points.setdefault(current_time, [])
        temp_list.append(temp_report)

    report_window.destroy()


def initialize_report_data_window(report_window, gas_station):
    Label(report_window, text="How much did you wait? Note: Use (h/mins)", fg="#242582", bg="#FFFFFB",
          font="Serif 10 bold").grid(row=0, column=0, padx=20,
                                     pady=(50, 0), sticky="w")
    waiting_time_entry = Entry(report_window)
    waiting_time_entry.grid(row=0, column=1, pady=(50, 0))

    Label(report_window, text="What was the price per Litre? (Format: xxxxx)", fg="#242582", bg="#FFFFFB",
          font="Serif 10 bold").grid(row=1, column=0, padx=20,
                                     pady=(10, 0), sticky="w")
    price_per_litre_entry = Entry(report_window)
    price_per_litre_entry.grid(row=1, column=1, pady=(10, 0))

    Button(report_window, text="Submit", width=20, font="Serif 11", fg="#FFFFFB", bg="#E12836",
           activebackground="#8B0000", bd=0,
           command=lambda: add_data_point(gas_station, waiting_time_entry, price_per_litre_entry, report_window)).grid(
        row=2, column=0,
        columnspan=2,
        padx=(40, 0),
        pady=(20, 0))


def open_report_window(gas_station, gas_stations_window):
    report_window = Toplevel(gas_stations_window)
    report_window.geometry("500x200")
    report_window.title("Report")
    report_window.configure(background="#FFFFFB")
    report_window.iconbitmap("logo.ico")
    report_window.resizable(width=False, height=False)
    initialize_report_data_window(report_window, gas_station)
    report_window.mainloop()


def display_stations(gas_stations, gas_stations_window):
    for child in gas_station_frames:
        child.destroy()
    gas_station_frames.clear()
    for station in gas_stations:
        gas_station_frame = Frame(second_frame, height=100, bg="#083EFD")
        gas_station_frame.pack(fill=X, expand=1, pady=(0, 10))
        Label(gas_station_frame, text="Name: " + station.__getattribute__("name"), width=80, anchor="w",
              font="Serif 10 bold", bg="#083EFD", fg="#FFFFFB",
              justify="left", relief=FLAT).place(x=10, y=10)
        Label(gas_station_frame, text="Opening hours: " + station.__getattribute__("opening_hours"), width=80,
              anchor="w",
              font="Serif 10 bold", bg="#083EFD", fg="#FFFFFB",
              justify="left", relief=FLAT).place(x=10, y=30)
        Label(gas_station_frame, text="Gas remaining: " + station.__getattribute__("gas_remaining"), width=80,
              anchor="w",
              font="Serif 10 bold", bg="#083EFD", fg="#FFFFFB",
              justify="left", relief=FLAT).place(x=10, y=50)
        Label(gas_station_frame, text="Price per Litre: " + str(station.__getattribute__("price_per_litre")), width=80,
              anchor="w",
              font="Serif 10 bold", bg="#083EFD", fg="#FFFFFB",
              justify="left", relief=FLAT).place(x=10, y=70)
        Button(gas_station_frame, text="Report", font="Serif 11", width=10, fg="#FFFFFB", bg="#E12836",
               activebackground="#8B0000", bd=0,
               command=partial(open_report_window, station, gas_stations_window)).place(x=555, y=30, height=35)

        gas_station_frames.append(gas_station_frame)


def initialize_search_frame(search_frame):
    search_bar_label = Label(search_frame, text="Search:", font="Serif 12", height=1, bg="#242582", fg="#FFFFFB")
    search_bar_label.place(x=10, y=15)

    search_bar = Entry(search_frame, textvariable=find_gas_station, width=78)
    search_bar.place(x=120, y=13, height=25)

    apply_filters_label = Label(search_frame, text="Apply filters:", font="Serif 12", height=1, bg="#242582",
                                fg="#FFFFFB")
    apply_filters_label.place(x=10, y=45)

    min_distance_option_menu = OptionMenu(search_frame, min_distance, "<= 1 km", "<= 5 km", "<= 10 km", "<= 25 km",
                                          "<= 50 km")
    min_distance_option_menu.configure(relief=GROOVE)
    min_distance_option_menu.configure(bd=0, width=10)
    min_distance_option_menu.place(x=120, y=45)

    is_open_option_menu = OptionMenu(search_frame, is_open, "Yes", "No")
    is_open_option_menu.configure(bd=0, width=10, relief=GROOVE)
    is_open_option_menu.place(x=230, y=45)

    waiting_times = []
    waiting_times.append("30 mins")
    mins = 60
    counter = 0
    full_hour = True
    while counter < 10:
        if full_hour:
            waiting_times.append(str(int(mins / 60)) + " h")
            full_hour = False
        else:
            waiting_times.append(str(int(mins / 60)) + " h" + " 30 mins")
            full_hour = True
        mins += 30
        counter += 1

    max_waiting_time_option_menu = OptionMenu(search_frame, max_waiting_time, *waiting_times)
    max_waiting_time_option_menu.configure(bd=0, width=15, relief=GROOVE)
    max_waiting_time_option_menu.place(x=340, y=45)

    amount_of_gas_option_menu = OptionMenu(search_frame, amount_of_gas, "NONE", "LOW", "MEDIUM", "HIGH")
    amount_of_gas_option_menu.configure(bd=0, width=12, relief=GROOVE)
    amount_of_gas_option_menu.place(x=480, y=45)

    Button(search_frame, text="Search", command=search_and_apply_filters, relief=GROOVE, bd=0, fg="#FFFFFB",
           bg="#E12836", activebackground="#8B0000", width=8).place(x=600, y=13, height=25)


def initialize_gas_stations_window(gas_stations_window):
    main_frame = Frame(gas_stations_window)
    main_frame.pack(fill=BOTH, expand=1)

    my_canvas = Canvas(main_frame)
    my_canvas.pack(side=LEFT, fill=BOTH, expand=1)
    my_canvas.bind_all("<MouseWheel>", lambda event: _on_mouse_wheel(event, my_canvas))

    my_scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL, command=my_canvas.yview)
    my_scrollbar.pack(side=RIGHT, fill=Y)

    my_canvas.configure(yscrollcommand=my_scrollbar.set)
    my_canvas.bind("<Configure>", lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))

    global second_frame
    second_frame = Frame(my_canvas, bg="#2F2FA2")

    my_canvas.create_window((0, 0), window=second_frame, anchor="nw")

    search_frame = LabelFrame(second_frame, bd=0, bg="#242582", width=700, height=80)
    search_frame.pack(fill=X, expand=True, pady=(0, 10))
    search_frame.pack_propagate(0)
    initialize_search_frame(search_frame)

    display_stations(gas_stations, gas_stations_window)


def get_current_time():
    components = time.ctime(time.time()).split(" ")[3]
    time_components = components.split(":")
    hour = int(time_components[0])
    minutes = int(time_components[1])
    return hour + (minutes / 60.0)


def get_day():
    components = time.ctime(time.time()).split(" ")
    return components[0]


def get_distance(lat1, lat2, lon1, lon2):
    lon1 = math.radians(lon1)
    lon2 = math.radians(lon2)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.pow(math.sin(dlat / 2), 2) + math.cos(lat1) * math.cos(lat2) * math.pow(math.sin(dlon / 2), 2);

    c = 2 * math.asin(math.sqrt(a))

    r = 6371

    return c * r


def get_my_latlng():
    return geocoder.ip('me').latlng


def convert_string_to_time(string):
    components = string.lower().split(" ")
    total_minutes = 0

    for i in range(0, len(components), 2):
        if components[i + 1] == "h":
            total_minutes += int(components[i]) * 60
        else:
            total_minutes += int(components[i])

    return total_minutes


def get_expected_waiting_time(gas_station):
    time_data_points = gas_station.__getattribute__("time_data_points")

    if len(time_data_points) == 0:
        return -1

    data_points = []
    sum_of_weights = 0.0
    current_time = get_current_time()

    for time, list in time_data_points.items():
        for report in list:
            weight = 12 - get_difference(float(time), current_time)
            sum_of_weights += weight
            data_points.append((weight, report.__getattribute__("waiting_time")))

    expected_waiting_time = 0
    for [weight, waiting_time] in data_points:
        expected_waiting_time += (weight / sum_of_weights) * waiting_time

    return expected_waiting_time


def get_difference(t1, t2):
    return min(
        abs(t1 - t2),
        abs(t1 - t2 + 24),
        abs(t1 - t2 - 24)
    )


def search_and_apply_filters():
    global gas_stations
    temp_gas_stations = gas_stations
    if len(find_gas_station.get()) != 0:
        find_name = find_gas_station.get().lower()
        temp_stations = []
        for station in temp_gas_stations:
            temp_attribute = station.__getattribute__("name").lower()
            if temp_attribute == find_name or temp_attribute.find(find_name) != -1:
                temp_stations.append(station)
        temp_gas_stations = list(temp_stations)

    if min_distance.get() != "Min Distance":
        min = int(min_distance.get().split(" ")[1])
        my_latlng = get_my_latlng()
        temp_stations = []
        for station in temp_gas_stations:
            if get_distance(station.__getattribute__("location")[0], my_latlng[0],
                            station.__getattribute__("location")[1], my_latlng[1]) <= min:
                temp_stations.append(station)
        temp_gas_stations = list(temp_stations)

    if is_open.get() != "Is Open":
        temp_bool = is_open.get()
        temp_stations = []
        for station in temp_gas_stations:
            if station.get_is_open() == temp_bool:
                temp_stations.append(station)
        temp_gas_stations = list(temp_stations)

    if max_waiting_time.get() != "Max Waiting Time":
        waiting_time = convert_string_to_time(max_waiting_time.get())
        temp_stations = []
        for station in gas_stations:
            expected_waiting_time = get_expected_waiting_time(station)
            if expected_waiting_time != -1 and expected_waiting_time <= waiting_time:
                temp_stations.append(station)
        temp_gas_stations = list(temp_stations)

    if amount_of_gas.get() != "Amount of Gas":
        temp_amount_of_gas = amount_of_gas.get()
        temp_stations = []
        for station in temp_gas_stations:
            if station.__getattribute__("gas_remaining") == temp_amount_of_gas:
                temp_stations.append(station)
        temp_gas_stations = list(temp_stations)

    if len(temp_gas_stations) == 0:
        messagebox.showinfo("Station Not Found",
                            "There is no station matching the name you have entered or the filters you have applied!")
        return
    display_stations(temp_gas_stations, gas_stations_window)


def get_stations():
    gas_stations_file = open("gas_stations.txt", mode="r", encoding="utf-8")
    json_string = ""
    temp_string = gas_stations_file.readline()
    while len(temp_string) != 0:
        temp_string = temp_string.strip("\n")
        json_string += temp_string
        temp_string = gas_stations_file.readline()

    if len(json_string) == 0:
        gas_stations = [
            GasStation("Zarazir", "from 7 to 12", "NONE", 35000, (33.876232795770015, 35.5612419203751), {}),
            GasStation("Lalipco - Baouchriyeh", "from 8 to 17", "LOW", 50000,
                       (33.87928169611985, 35.56157273696416), {}),
            GasStation("Lalipco - Sabtieh", "from 0 to 24", "HIGH", 80000,
                       (33.878242762713676, 35.55323865081171), {}),
            GasStation("Hypco - Dekwaneh", "from 10 to 17", "LOW", 45000,
                       (33.878389033747915, 35.54999269515389), {}),
            GasStation("United - Baouchriyeh", "from 9 to 17", "HIGH", 70000,
                       (33.88193353788926, 35.555835971842725), {}),
            GasStation("United - Dekwaneh", "from 9 to 17", "MEDIUM", 75000,
                       (33.87538685467578, 35.54773970167417), {}),
            GasStation("Dallas", "from 7 to 10", "NONE", 35000, (33.875355992315434, 35.54793231560126), {}),
            GasStation("Medco - Dekwaneh", "from 0 to 24", "LOW", 50000,
                       (33.87994464030376, 35.541369462837096), {}),
            GasStation("Caltex - Sin El Fil", "from 10 to 17", "HIGH", 80000,
                       (33.873412115974794, 35.54116112342966), {}),
            GasStation("Hypco - Sin El Fil", "from 10 to 17", "LOW", 45000,
                       (33.86907296503052, 35.54293504860818), {}),
            GasStation("Medco - Ashrafieh", "from 5 to 22", "HIGH", 70000,
                       (33.891802181572146, 35.52303288199711), {}),
            GasStation("Wardieh - Sin El Fil", "from 0 to 24", "MEDIUM", 75000,
                       (33.88048979834946, 35.53207116220189), {}),
            GasStation("Alaytam", "from 10 to 17", "LOW", 90000,
                       (33.859186520696106, 35.51244552693504), {}),
            GasStation("Zouheiry", "from 9 to 17", "MEDIUM", 75000,
                       (33.859186520696106, 35.51244552693504), {}),
            GasStation("Alatrash", "from 6 to 17", "HIGH", 85000,
                       (33.84870406002121, 35.7104417635826), {}),
            GasStation("Lalipco", "from 1 to 18", "HIGH", 85000,
                       (33.84870406002121, 35.7104417635826), {}),
            GasStation("Hypco", "from 12 to 21", "HIGH", 85000,
                       (33.84870406002121, 35.7104417635826), {}),
            GasStation("Flayhan", "from 6 to 17", "HIGH", 85000,
                       (33.80101101483463, 35.68786527796499), {})]
        return gas_stations
    else:
        return jsonpickle.decode(json_string)


def _on_mouse_wheel(event, my_canvas):
    my_canvas.yview_scroll(-1 * int((event.delta / 120)), "units")


gas_stations_window = Tk()
gas_stations_window.geometry("700x500")
gas_stations_window.title("Gas Hub")
gas_stations_window.iconbitmap("logo.ico")
gas_stations_window.configure(background="#242582")
gas_stations_window.resizable(width=False, height=False)

global find_gas_station
find_gas_station = StringVar()
global min_distance
min_distance = StringVar()
min_distance.set("Min Distance")
global is_open
is_open = StringVar()
is_open.set("Is Open")
global amount_of_gas
amount_of_gas = StringVar()
amount_of_gas.set("Amount of Gas")
global max_waiting_time
max_waiting_time = StringVar()
max_waiting_time.set("Max Waiting Time")
global second_frame
global gas_station_frames
gas_station_frames = []
global gas_stations
gas_stations = get_stations()
initialize_gas_stations_window(gas_stations_window)


def on_closing():
    gas_stations_window.withdraw()
    thread = Thread(target=save_gas_stations_to_file)
    thread.daemon = True
    thread.start()


gas_stations_window.protocol("WM_DELETE_WINDOW", on_closing)

mainloop()
