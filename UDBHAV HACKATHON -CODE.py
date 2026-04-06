# ==========================
# Automated Energy-Grid Orchestrator
# Smart Campus Hackathon - Ghost Classroom Solution
# This code simulates an energy-saving system for classrooms.
# It's designed for beginners: simple, with lots of comments, and easy to understand.
# ==========================

import time
import random
from datetime import datetime, timedelta
from enum import Enum
import tkinter as tk
from tkinter import ttk, messagebox

# ==========================
# Simple Enums (like constants for choices)
# ==========================
class UserRole(Enum):
    ADMIN = "admin"          # Can do everything
    FACULTY = "faculty"      # Can override and view reports
    MAINTENANCE = "maintenance"  # Can handle alerts and view reports

class ApplianceStatus(Enum):
    ON = "on"                # System is running
    OFF = "off"              # System is off
    MALFUNCTION = "malfunction"  # Something is broken

# ==========================
# User Class (represents people using the system)
# ==========================
class User:
    def __init__(self, user_id, name, role):
        self.user_id = user_id  # Unique ID
        self.name = name        # Full name
        self.role = role        # Role (admin, faculty, etc.)

    def has_permission(self, action):
        # Check if this user can do a certain action
        if self.role == UserRole.ADMIN:
            return True  # Admins can do anything
        elif self.role == UserRole.FACULTY and action in ["override", "view_reports"]:
            return True  # Faculty can override systems and view reports
        elif self.role == UserRole.MAINTENANCE and action in ["maintenance_alert", "view_reports"]:
            return True  # Maintenance can see alerts and reports
        return False  # No permission

# ==========================
# Timetable Class (simulates a schedule database)
# ==========================
class Timetable:
    def __init__(self):
        # Sample schedule for rooms (in real life, this would come from a database)
        self.schedule = {
            "Room101": [
                {"start": "08:00", "end": "10:00", "class_size": 30, "subject": "Math"},
                {"start": "14:00", "end": "16:00", "class_size": 25, "subject": "Physics"}
            ],
            "Room102": [
                {"start": "09:00", "end": "11:00", "class_size": 20, "subject": "Chemistry"}
            ],
            "Room103": []  # Empty room
        }

    def get_upcoming_classes(self, room, current_time):
        # Find classes starting soon in this room
        upcoming = []
        for cls in self.schedule.get(room, []):
            start_time = datetime.strptime(cls["start"], "%H:%M").time()
            if start_time > current_time.time():  # If class starts after now
                upcoming.append(cls)
        return upcoming

    def get_current_class(self, room, current_time):
        # Check if there's a class happening now
        for cls in self.schedule.get(room, []):
            start_time = datetime.strptime(cls["start"], "%H:%M").time()
            end_time = datetime.strptime(cls["end"], "%H:%M").time()
            if start_time <= current_time.time() <= end_time:  # If now is during class
                return cls
        return None  # No class now

# ==========================
# Room Class (represents a classroom with sensors and systems)
# ==========================
class Room:
    def __init__(self, room_id):
        self.room_id = room_id
        self.occupancy = False  # Is someone in the room? (True/False)
        self.ambient_light = 500  # Light level (lux)
        self.temperature = 22     # Room temperature (Celsius)
        self.hvac_status = ApplianceStatus.ON  # HVAC (heating/cooling) status
        self.lights_status = ApplianceStatus.ON  # Lights status
        self.last_occupied_time = datetime.now()  # Last time someone was here
        self.empty_timer = 0  # Minutes since room became empty
        self.maintenance_alerts = []  # List of problems

    def update_sensors(self):
        # Simulate real sensors (in real life, this would read from IoT devices)
        self.occupancy = random.choice([True, False])  # Randomly set if occupied
        self.ambient_light = random.randint(100, 1000)  # Random light level
        self.temperature = random.randint(18, 28)       # Random temperature
        # Sometimes, simulate a malfunction
        if random.random() < 0.05:  # 5% chance
            if random.choice([True, False]):
                self.hvac_status = ApplianceStatus.MALFUNCTION
                self.maintenance_alerts.append(f"HVAC broken in {self.room_id}")
            else:
                self.lights_status = ApplianceStatus.MALFUNCTION
                self.maintenance_alerts.append(f"Lights broken in {self.room_id}")

    def pre_condition(self, class_size):
        # Adjust temperature before class based on how many students
        if class_size > 30:
            self.temperature = 20  # Cooler for big class
        elif class_size > 20:
            self.temperature = 22  # Normal
        else:
            self.temperature = 24  # Warmer for small class
        print(f"Pre-conditioned {self.room_id} to {self.temperature}°C for {class_size} students")

# ==========================
# EnergyAnalytics Class (tracks energy use and savings)
# ==========================
class EnergyAnalytics:
    def __init__(self):
        self.daily_usage = {}  # Usage per hour
        self.weekly_savings = 0  # Estimated savings

    def log_usage(self, rooms):
        # Count how many rooms have systems on
        current_hour = datetime.now().hour
        usage = sum(1 for room in rooms.values() if room.hvac_status == ApplianceStatus.ON or room.lights_status == ApplianceStatus.ON)
        if current_hour not in self.daily_usage:
            self.daily_usage[current_hour] = 0
        self.daily_usage[current_hour] += usage

    def generate_report(self):
        # Print a simple energy report
        total_daily = sum(self.daily_usage.values())
        print(f"\n[Energy Report] Total daily usage: {total_daily} units")
        print("Usage by hour:")
        for hour, usage in sorted(self.daily_usage.items()):
            print(f"  Hour {hour}: {usage} units")
        # Estimate savings (simple calculation)
        potential_savings = len(self.daily_usage) * 24 * 0.4  # 40% savings estimate
        print(f"Estimated weekly savings: {potential_savings} units")

# ==========================
# EnergyOrchestrator Class (the main brain of the system)
# ==========================
class EnergyOrchestrator:
    def __init__(self):
        # Create 3 rooms for simplicity
        self.rooms = {f"Room{101+i}": Room(f"Room{101+i}") for i in range(3)}
        self.timetable = Timetable()  # Schedule
        self.analytics = EnergyAnalytics()  # Energy tracker
        self.emergency_mode = False  # Special mode for emergencies
        # Sample users
        self.users = {
            "admin1": User("admin1", "Admin User", UserRole.ADMIN),
            "faculty1": User("faculty1", "Dr. Smith", UserRole.FACULTY),
            "maint1": User("maint1", "Tech Support", UserRole.MAINTENANCE)
        }
        self.current_user = None  # Who is logged in

    def login(self, user_id):
        # Log in a user
        if user_id in self.users:
            self.current_user = self.users[user_id]
            print(f"Logged in as {self.current_user.name} ({self.current_user.role.value})")
            return True
        print("Invalid user ID")
        return False

    def monitor_and_control(self, current_time):
        # Check each room and control systems
        for room in self.rooms.values():
            room.update_sensors()  # Update sensor data

            if room.occupancy:  # If someone is in the room
                room.last_occupied_time = current_time
                room.empty_timer = 0  # Reset empty timer
                if not self.emergency_mode:
                    room.hvac_status = ApplianceStatus.ON  # Turn on HVAC
                    # Turn on lights only if dark
                    if room.ambient_light < 300:
                        room.lights_status = ApplianceStatus.ON
                    else:
                        room.lights_status = ApplianceStatus.OFF
            else:  # Room is empty
                room.empty_timer += 5  # Add 5 minutes
                if room.empty_timer >= 15 and not self.emergency_mode:
                    room.hvac_status = ApplianceStatus.OFF  # Turn off after 15 mins
                    room.lights_status = ApplianceStatus.OFF
                    print(f"{room.room_id} turned off (idle for 15 mins)")

            # Predictive: Prepare room for upcoming class
            upcoming = self.timetable.get_upcoming_classes(room.room_id, current_time)
            if upcoming:
                next_class = upcoming[0]
                time_diff = (datetime.combine(current_time.date(), datetime.strptime(next_class["start"], "%H:%M").time()) - current_time).seconds / 60
                if time_diff <= 30:  # If class starts in 30 mins or less
                    room.pre_condition(next_class["class_size"])

            # Check for maintenance issues
            if room.maintenance_alerts:
                if self.current_user and self.current_user.has_permission("maintenance_alert"):
                    for alert in room.maintenance_alerts:
                        print(f"[ALERT] {alert}")
                room.maintenance_alerts.clear()  # Clear alerts after checking

        self.analytics.log_usage(self.rooms)  # Log energy use

    def manual_override(self, room_id, action):
        # Allow manual control (e.g., faculty can turn on/off)
        if not self.current_user or not self.current_user.has_permission("override"):
            print("No permission to override")
            return
        if room_id not in self.rooms:
            print("Room not found")
            return
        room = self.rooms[room_id]
        if action.lower() == "on":
            room.hvac_status = ApplianceStatus.ON
            room.lights_status = ApplianceStatus.ON
            print(f"{room_id} manually turned ON")
        elif action.lower() == "off":
            room.hvac_status = ApplianceStatus.OFF
            room.lights_status = ApplianceStatus.OFF
            print(f"{room_id} manually turned OFF")

    def get_room_status_text(self):
        # Build a text summary of each room for the GUI
        lines = []
        for room in self.rooms.values():
            lines.append(
                f"{room.room_id}: Occupied={room.occupancy}, Light={room.ambient_light} lux, "
                f"Temp={room.temperature}°C, HVAC={room.hvac_status.value}, Lights={room.lights_status.value}"
            )
        return "\n".join(lines)

    def emergency_mode(self, activate):
        # Turn everything on in emergencies
        self.emergency_mode = activate
        status = "ON" if activate else "OFF"
        print(f"Emergency mode {status}")
        if activate:
            for room in self.rooms.values():
                room.hvac_status = ApplianceStatus.ON
                room.lights_status = ApplianceStatus.ON

    def run_simulation(self):
        # Run a simple 2-hour simulation
        print("=== Starting Energy Orchestrator Simulation ===")
        self.login("admin1")  # Log in as admin
        simulated_time = datetime(2024, 4, 6, 8, 0)  # Start at 8 AM
        minutes = 0
        while minutes < 120:  # 120 minutes = 2 hours
            print(f"\n--- Time: {simulated_time.strftime('%H:%M')} (Minute {minutes}) ---")
            self.monitor_and_control(simulated_time)

            # Sometimes, simulate a faculty override (fixed to check permission)
            if random.random() < 0.2:  # 20% chance
                if self.current_user and self.current_user.has_permission("override"):
                    self.manual_override("Room101", random.choice(["on", "off"]))

            time.sleep(0.5)  # Pause for demo
            minutes += 5
            simulated_time += timedelta(minutes=5)

        print("\nSimulation done!")
        self.analytics.generate_report()  # Final report only

class SmartCampusGUI:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.root = tk.Tk()
        self.root.title("Smart Campus Energy Orchestrator")
        self.root.geometry("620x420")

        self.user_var = tk.StringVar(value="admin1")
        self.status_label = None

        self._build_ui()
        self._refresh_status()

    def _build_ui(self):
        top_frame = ttk.Frame(self.root, padding=12)
        top_frame.pack(fill="x")

        ttk.Label(top_frame, text="Choose User:").grid(row=0, column=0, sticky="w")
        user_menu = ttk.OptionMenu(top_frame, self.user_var, self.user_var.get(), *self.orchestrator.users.keys())
        user_menu.grid(row=0, column=1, sticky="w", padx=(8, 0))

        ttk.Button(top_frame, text="Login", command=self._handle_login).grid(row=0, column=2, padx=8)
        ttk.Button(top_frame, text="Refresh Status", command=self._refresh_status).grid(row=0, column=3, padx=8)
        ttk.Button(top_frame, text="Run Update", command=self._run_update).grid(row=0, column=4, padx=8)

        status_frame = ttk.LabelFrame(self.root, text="Room Status", padding=12)
        status_frame.pack(fill="both", expand=True, padx=12, pady=(8, 12))

        self.status_label = tk.Text(status_frame, wrap="word", height=16, state="disabled")
        self.status_label.pack(fill="both", expand=True)

        button_frame = ttk.Frame(self.root, padding=12)
        button_frame.pack(fill="x")

        ttk.Button(button_frame, text="Run Simulation", command=self._run_simulation_from_gui).pack(side="left")
        ttk.Button(button_frame, text="Show Energy Report", command=self._show_report).pack(side="left", padx=8)

    def _handle_login(self):
        user_id = self.user_var.get()
        if self.orchestrator.login(user_id):
            messagebox.showinfo("Login", f"Logged in as {self.orchestrator.current_user.name}")
        else:
            messagebox.showerror("Login Failed", "Invalid user ID")
        self._refresh_status()

    def _run_update(self):
        current_time = datetime.now()
        self.orchestrator.monitor_and_control(current_time)
        self._refresh_status()

    def _refresh_status(self):
        status = self.orchestrator.get_room_status_text()
        self.status_label.config(state="normal")
        self.status_label.delete("1.0", "end")
        self.status_label.insert("1.0", status)
        self.status_label.config(state="disabled")

    def _run_simulation_from_gui(self):
        self.orchestrator.run_simulation()
        self._refresh_status()
        messagebox.showinfo("Simulation", "Simulation completed. Check console for details.")

    def _show_report(self):
        report_lines = [f"Hour {hour}: {usage} units" for hour, usage in sorted(self.orchestrator.analytics.daily_usage.items())]
        report = "\n".join(report_lines) or "No data yet. Run an update first."
        messagebox.showinfo("Energy Report", report)

    def run(self):
        self.root.mainloop()

# ==========================
# Run the Program
# ==========================
if __name__ == "__main__":
    # Create and start the system
    system = EnergyOrchestrator()
    gui = SmartCampusGUI(system)
    gui.run()