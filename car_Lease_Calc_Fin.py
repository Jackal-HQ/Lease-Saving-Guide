import sqlite3
import customtkinter
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from PIL import Image

# Database Stuff ---------
# Connect to the SQLite database and return connection and cursor
def connect_to_db():
    conn = sqlite3.connect('car_lease.db')
    cursor = conn.cursor()
    return conn, cursor

# Fetch cars from the database
def get_cars_from_db(cursor):
    cursor.execute('SELECT * FROM cars')
    return cursor.fetchall()

# Car class for the lease calculator
class Car:
    def __init__(self, make, model, base_price, lease_term, interest_rate, down_payment, mileage, residual_percentage):
        self.make = make
        self.model = model
        self.base_price = base_price
        self.lease_term = lease_term
        self.interest_rate = interest_rate
        self.down_payment = down_payment
        self.mileage = mileage
        self.residual_percentage = residual_percentage if residual_percentage is not None else 0.50  # Default 50%
        self.residual_value = self.base_price * self.residual_percentage  # Calculate residual value

    def calculate_lease(self):
        # Capitalized cost: Base price + fees - down payment
        capitalized_cost = self.base_price + 3000 + 500 + 499 - self.down_payment

        # Money factor: Interest rate / 2400
        money_factor = self.interest_rate / 2400

        # Monthly depreciation: (Capitalized cost - Residual value) / Lease term
        monthly_depreciation = (capitalized_cost - self.residual_value) / self.lease_term

        # Monthly finance charge: (Capitalized cost + Residual value) * Money factor
        monthly_finance_charge = (capitalized_cost + self.residual_value) * money_factor

        # Total monthly lease payment
        monthly_payment = monthly_depreciation + monthly_finance_charge

        return round(monthly_payment, 2)

# Insurance Calculator Class
class InsuranceCalculator:
    def __init__(self, user_profile, car):
        self.user_profile = user_profile
        self.car = car

    def calculate_insurance(self):
        # Base rate for insurance
        base_rate = 500

        # Age factor
        if self.user_profile.age < 25:
            base_rate += 100
        elif self.user_profile.age > 60:
            base_rate += 50
        else:
            base_rate -= 50

        # Driving history factor
        if self.user_profile.driving_history == "clean":
            base_rate -= 100
        elif self.user_profile.driving_history == "minor":
            base_rate += 100
        elif self.user_profile.driving_history == "major":
            base_rate += 200

        # Car price factor
        if self.car.base_price > 30000:
            base_rate += 200

        # Location factor
        if self.user_profile.location == "urban":
            base_rate += 150
        elif self.user_profile.location == "suburban":
            base_rate += 50
        elif self.user_profile.location == "rural":
            base_rate -= 50

        return round(base_rate, 2)

# User profile for insurance calculator
class UserProfile:
    def __init__(self, age, driving_history, location):
        self.age = age
        self.driving_history = driving_history
        self.location = location

# Scrollable frame for car selection
class ScrollCarFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, item_list, command=None, **kwargs):
        super().__init__(master, **kwargs)

        self.command = command
        self.radiobutton_variable = customtkinter.StringVar()
        self.radiobutton_list = []
        for i, item in enumerate(item_list):
            self.add_item(item)

    def add_item(self, item):
        radiobutton = customtkinter.CTkRadioButton(self, text=item, value=item, variable=self.radiobutton_variable)
        if self.command is not None:
            radiobutton.configure(command=self.command)
        radiobutton.grid(row=len(self.radiobutton_list), column=0, pady=(0, 10))
        self.radiobutton_list.append(radiobutton)

    def get_checked_item(self):
        return self.radiobutton_variable.get()

# Frame to show the lease output and trigger calculations
class LeaseOutPutFrame(customtkinter.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        
        def click_lease():
            self.app.calculate_lease_and_insurance()

        self.label = customtkinter.CTkLabel(master=self, text=" ", font=("Arial", 20))
        self.label.pack(anchor="n", expand=True, pady=10, padx=30)
        
        self.btn = customtkinter.CTkButton(master=self, text="Calculate Lease", command=click_lease, corner_radius=20)
        self.btn.pack(anchor="center", expand=True, pady=10, padx=30)

# Main Application Class
class LeaseCalculatorApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Set the window title and layout
        self.title("Lease Calculator")
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(3, weight=1)

        # Language dictionaries
        self.text = {
            'en': {
                'title': "Lease Calculator",
                'calculate_lease': "Calculate Lease",
                'enter_down_payment': "Enter Down Payment amount: ",
                'enter_age': "Enter your age: ",
                'driving_history': "Driving History",
                'location': "Location",
                'months': "Months",
                'translate': "Translate to Spanish"
            },
            'es': {
                'title': "Calculadora de Arrendamiento",
                'calculate_lease': "Calcular Arrendamiento",
                'enter_down_payment': "Ingrese el monto del pago inicial: ",
                'enter_age': "Ingrese su edad: ",
                'driving_history': "Historial de manejo",
                'location': "Ubicación",
                'months': "Meses",
                'translate': "Traducir al inglés"
            }
        }

        # Current language variable
        self.current_language = 'en'

        # Connect to the database and fetch car data
        self.conn, self.cursor = connect_to_db()
        self.cars = get_cars_from_db(self.cursor)

        # Scrollable frame for car selection
        self.scrollable_radiobutton_frame = ScrollCarFrame(
            master=self, width=500, command=self.radiobutton_frame_event,
            item_list=[f"{car[0]}. {car[1]} {car[2]} - ${car[3]} (Residual Value: {round((car[7] * 100) if car[7] is not None else 'N/A')}% of base price)" for car in self.cars]
        )
        self.scrollable_radiobutton_frame.grid(row=0, column=0, padx=15, pady=15, sticky="ns", rowspan=2)

        # Lease info frame
        self.lease_info_frame = LeaseInfoFrame(master=self)
        self.lease_info_frame.grid(row=0, column=1, padx=15, pady=15)
        self.lease_info_frame.configure(fg_color="#8D6F3A", border_color="#FFCC70", border_width=2)

        # Down payment frame
        self.down_payment_frame = DownPayFrame(master=self)
        self.down_payment_frame.grid(row=1, column=1, padx=15, pady=15)
        self.down_payment_frame.configure(fg_color="#8D6F3A", border_color="#FFCC70", border_width=2)

        # User profile info frame
        self.user_info_frame = UserClassFrame(master=self)
        self.user_info_frame.grid(row=0, column=2, padx=15, pady=15, sticky="ns", rowspan=2)
        self.user_info_frame.configure(fg_color="#8D6F3A", border_color="#FFCC70", border_width=2)
        
        #Piggy bank frame
        self.pig_frame = PigBankFrame(master=self)
        self.pig_frame.grid(row=2, column=0, padx=15, pady=15, sticky="ns")
        self.pig_frame.configure( fg_color="#8D6F3A", border_color="#FFCC70", border_width=2)

        # Lease output frame (to show the calculation results)
        self.lease_output_frame = LeaseOutPutFrame(master=self, app=self)
        self.lease_output_frame.grid(row=2, column=1, padx=15, pady=15, sticky="ns")
        self.lease_output_frame.configure(fg_color="#8D6F3A", border_color="#FFCC70", border_width=2)

        # Pie chart frame (for visual representation)
        self.figure = plt.Figure(figsize=(4, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.pie_chart_canvas = FigureCanvasTkAgg(self.figure, self)
        self.pie_chart_canvas.get_tk_widget().grid(row=2, column=2, padx=15, pady=15, sticky="ns")

        # Language toggle button
        self.translate_button = customtkinter.CTkButton(
            master=self, text=self.text[self.current_language]['translate'], command=self.toggle_language
        )
        self.translate_button.grid(row=3, column=0, padx=15, pady=15)

    def radiobutton_frame_event(self):
        print(f"Chosen Car: {self.scrollable_radiobutton_frame.get_checked_item()}")

    def toggle_language(self):
        """Toggle between English and Spanish."""
        self.current_language = 'es' if self.current_language == 'en' else 'en'
        self.update_ui_language()

    def update_ui_language(self):
        """Update the UI elements to reflect the current language."""
        self.title(self.text[self.current_language]['title'])
        self.lease_output_frame.btn.configure(text=self.text[self.current_language]['calculate_lease'])
        self.down_payment_frame.label.configure(text=self.text[self.current_language]['enter_down_payment'])
        self.user_info_frame.age_label.configure(text=self.text[self.current_language]['enter_age'])
        self.user_info_frame.d_label.configure(text=self.text[self.current_language]['driving_history'])
        self.user_info_frame.l_label.configure(text=self.text[self.current_language]['location'])
        self.lease_info_frame.label.configure(text=self.text[self.current_language]['months'])
        self.translate_button.configure(text=self.text[self.current_language]['translate'])

    def calculate_lease_and_insurance(self):
        """Calculate the lease, insurance, and display results."""
        try:
            selected_car_text = self.scrollable_radiobutton_frame.get_checked_item()
            selected_car_index = int(selected_car_text.split('.')[0]) - 1
            selected_car = self.cars[selected_car_index]
            
            # Extract values from frames
            down_payment = float(self.down_payment_frame.entry.get())
            lease_term = int(self.lease_info_frame.slider.get())
            user_age = int(self.user_info_frame.age_entry.get())
            driving_history = self.user_info_frame.d_combo.get().strip().lower()
            location = self.user_info_frame.l_combo.get().strip().lower()

            # Create Car object and calculate lease
            car = Car(make=selected_car[1], model=selected_car[2], base_price=selected_car[3],
                      lease_term=lease_term, interest_rate=selected_car[5],
                      down_payment=down_payment, mileage=selected_car[6], residual_percentage=selected_car[7])
            self.monthly_lease_payment = car.calculate_lease()

            # Create user profile object
            user_profile = UserProfile(age=user_age, driving_history=driving_history, location=location)

            # Calculate insurance
            insurance_calculator = InsuranceCalculator(user_profile, car)
            self.monthly_insurance_payment = insurance_calculator.calculate_insurance()

            # Total monthly cost
            self.total_monthly_cost = self.monthly_lease_payment + self.monthly_insurance_payment

            # Calculate recommended income (assuming 15% of income goes to car expenses)
            self.recommended_income = self.total_monthly_cost / 0.15

            # Display the results
            self.lease_output_frame.label.configure(
                text=f"Monthly Lease Payment: ${self.monthly_lease_payment}\n"
                     f"Monthly Insurance Payment: ${self.monthly_insurance_payment}\n"
                     f"Total Monthly Cost: ${self.total_monthly_cost}\n"
                     f"Recommended Monthly Income: ${round(self.recommended_income, 2)}"
            )

            # Update the pie chart
            self.update_pie_chart()

        except ValueError:
            messagebox.showerror("Input Error", "Please make sure all inputs are valid.")

    def update_pie_chart(self):
        """Update the pie chart with the lease, insurance, and remaining income breakdown."""
        remaining_income = self.recommended_income - self.total_monthly_cost
        labels = ['Lease Payment', 'Insurance Payment', 'Remaining Income']
        sizes = [self.monthly_lease_payment, self.monthly_insurance_payment, remaining_income]
        colors = ['#ff9999', '#66b3ff', '#99ff99']

        self.ax.clear()
        self.ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        self.ax.axis('equal')  # Equal aspect ratio ensures the pie is circular
        self.pie_chart_canvas.draw()

# Down payment frame
class DownPayFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.label = customtkinter.CTkLabel(master=self, text="Enter Down Payment amount: ")
        self.label.pack(anchor="n", expand=True, pady=10, padx=30)
        self.entry = customtkinter.CTkEntry(master=self,placeholder_text="$...")
        self.entry.pack(anchor="s", expand=True,pady=10, padx=30)

# Piggy Bank Frame
class PigBankFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        pig = Image.open("images/piggy_bank_PNG35.png")
        
        self.count = 0

        def click_pig():
            print(f"Entered Value: {self.p_entry.get()}")
            self.count += int(self.p_entry.get())
            self.label.configure(text=f"You have saved up ${self.count}")
            
        self.label = customtkinter.CTkLabel(master=self,text="No money saved", font=("Arial", 20))
        self.label.pack(anchor="n", expand=True, pady=10, padx=30)

        self.p_entry = customtkinter.CTkEntry(master=self,placeholder_text="$...")
        self.p_entry.pack(anchor="s", expand=True,pady=10, padx=30)

        self.btn = customtkinter.CTkButton(master=self, text="Submit", command=click_pig, corner_radius=20,image=customtkinter.CTkImage(pig))
        self.btn.pack(anchor="s",expand=True,pady=10, padx=30)

# Lease info frame
class LeaseInfoFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        def slider_event(value):
            self.label.configure(text=f"{int(value)} Months")
        
        self.slider = customtkinter.CTkSlider(master=self, from_=24, to=60, number_of_steps=3, command=slider_event)
        self.slider.pack(anchor="s", expand=True, pady=10, padx=30)
        self.label = customtkinter.CTkLabel(master=self, text=f"{self.slider.get()} Months")
        self.label.pack(anchor="n", expand=True, pady=10, padx=30)

# User info frame
class UserClassFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.age_label = customtkinter.CTkLabel(master=self, text="Enter your age: ")
        self.age_label.pack(anchor="n", expand=True, pady=10, padx=30)
        self.age_entry = customtkinter.CTkEntry(master=self, placeholder_text="")
        self.age_entry.pack(anchor="s", expand=True, pady=10, padx=30)
        
        self.d_label = customtkinter.CTkLabel(master=self, text="Driving History")
        self.d_label.pack(anchor="n", expand=True, pady=10, padx=30)
        self.d_combo = customtkinter.CTkComboBox(master=self, values=["clean", "minor", "major"])
        self.d_combo.pack(anchor="n", expand=True, pady=10, padx=30)
        
        self.l_label = customtkinter.CTkLabel(master=self, text="Location")
        self.l_label.pack(anchor="n", expand=True, pady=10, padx=30)
        self.l_combo = customtkinter.CTkComboBox(master=self, values=["urban", "suburban", "rural"])
        self.l_combo.pack(anchor="n", expand=True, pady=10, padx=30)

# Run the application
app = LeaseCalculatorApp()
app.mainloop()
