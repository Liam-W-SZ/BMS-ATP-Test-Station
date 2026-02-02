import customtkinter as ctk
import json
import os
from main import BMSCommunicator
from CTkMessagebox import CTkMessagebox
from PIL import Image
import datetime
import time
from tv_tools import root,outputJSON,outputJSON_local
from tv_tools import test,store_pack_info
#from tv_tools import curlPost #Jaspers Datalog output function - removed
from tv_tools import maskCheck
from tv_tools import load_ftp_file
from tv_tools import send_test_data
import re
import ftplib
import random

# Set appearance and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

global temp_user

class BMSTestApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("BMS Test Station")
        self.geometry("1200x900")
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        
        # Create sidebar frame
        self.sidebar = ctk.CTkFrame(self, width=300, height=600) #, fg_color="lightgray"
        self.sidebar.grid(row=0, column=0, padx=20, pady=(20, 20), sticky="new")

        # Create main content frame
        self.main_content = ctk.CTkFrame(self) #, fg_color="lightgray"
        self.main_content.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.current_operator = None
        self.tester = None
        
        # Replace lock icons with colored blocks
        self.lock_image = ctk.CTkButton(
            master=None,
            width=20,
            height=20,
            fg_color="red",
            text="",
            hover=False
        )
        self.unlock_image = ctk.CTkButton(
            master=None,
            width=20,
            height=20,
            fg_color="green",
            text="",
            hover=False
        )

        
        # #Load Production Config File from FTP Server
        # ftpfolder = 'BMS_Test_Station_New/config'
        # filename = 'Production_config.json'
        # json_data = json.loads(load_ftp_file(ftpfolder,filename).decode('utf-8'))
        # self.config = json_data
        # # Now 'file_data' contains the file's binary data in memory
        # #print(self.config)
        # #print(f"Successfully read data from {filename}.")
        # #From FTP Server Production

        
        # # Load RMA Config File from FTP Server
        # ftpfolder = 'BMS_Test_Station_New/config'
        # filename = 'RMA_config.json'
        # json_data = json.loads(load_ftp_file(ftpfolder,filename).decode('utf-8'))
        # self.configRMA = json_data
        # # Now 'file_data' contains the file's binary data in memory
        # #print(self.configRMA)
        # #print(f"Successfully read data from {filename}.")
        # #From FTP Server RMA
        

        # # Load Login Config File from FTP Server
        # ftpfolder = 'BMS_Test_Station_New/config'
        # filename = 'Login.json'
        # json_data = json.loads(load_ftp_file(ftpfolder,filename).decode('utf-8'))
        # self.configLogin = json_data
        # # Now 'file_data' contains the file's binary data in memory
        # #print(self.configLogin)
        # #print(f"Successfully read data from {filename}.")
        # #From FTP Server Login


        # Load local Production config file        
        NB_file = 'config.json'
        with open(NB_file, 'r') as f:
            self.config = json.load(f)        
        #Load local config folder
             

        # #Open local RMA config file         
        t_file = 'configRMA.json'
        with open(t_file, 'r') as f:
            self.configRMA = json.load(f)
            print(self.configRMA)
        # #Open local RMA config file     

        # #Open local Operator Login config file     
        login_file = 'Login.json'
        with open(login_file, 'r') as f:
            self.configLogin = json.load(f)
        # #Open local Operator Login config file 

        
        #Load local config folder
        # Start with disabled state
        self.start_button = None  # Will be initialized in setup_sidebar
        
        self.setup_sidebar()
        #self.setup_sidebar2()
        self.setup_main_content()

        #Liam Start
        self.ts = None
        self.current_operator = None
        self.test_desc = "System ATP - Battery Validation Test"  # Example attribute
        self.test_jig = "BMS Test Station Test Jig"
        self.device_id = "Device ID" #SZ-G8K2-9999999
        self.serialnr = "Serial Number" #"SZS:SZ-G8K2-9999999 / SC:405-1001160 / JN:MF999999"
        self.jobnr = "JN:MF999999" #JN:MF999999
        self.prefix = "NA"
        self.procedure = "BMS ATP Test"
        self.productGroup = "Batteries"
        self.supplierserial = "Supplier Serial" #"SP59B2308230186" - currrently sz Serial Number
        self.lowerlevelID = "NA"
        self.tests = []
        self.errors = []
        self.result = "Undetermined"  # Can be dynamic based on the test result
        
    filepath = os.path.join("data", 'pack_info.json') #works

    @staticmethod      
    def load_pack_info(filepath):
        #Load the pack information from the JSON file.
        try:
            # Open the JSON file in read mode
            with open(filepath, 'r') as json_file:
                # Load and parse the JSON data into a Python dictionary
                pack_info = json.load(json_file)
                #print(pack_info)
                return pack_info
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return None

       
    
    data = load_pack_info(filepath)
    device_info = data.get('Acquire Device Manufacture Info', {})
    supplier_info = device_info.get('Manufacturer', 'Unknown Device')
    device_name = device_info.get('Device  Name', 'Unknown Device') #get device name
    sup_serial_number = device_info.get('BMS Serial Number','Unknown Device') #get supplier serial number
    
    # output Pack_info to FTP server in complete_pack_data folder
    def store_test_data(self):

        #Store relevant test data into the global variables and create the TestFile1 object.        
        global ts, tester, testdesc, testjig, deviceid, serialnr, jobnr, prefix, procedure, productGroup, supplierserial, lowerlevelID, tests, errors, result,TestFile1

        ts = int(time.time()) #epoch time in seconds
        tester = self.current_operator if self.current_operator else "Unknown"  # Current operator or "Unknown" 
        testdesc = self.test_desc #default
        testjig = self.test_jig #Default
        deviceid = self.device_id#Get
        serialnr = self.serialnr #Get  self.device_id = parts[0] self.SC = parts[1]    self.jobnr  parts[2]
        jobnr = self.jobnr  # Assuming this is a constant or incremented elsewhere
        prefix = self.prefix  # Default prefix
        procedure = self.procedure  # Default procedure
        productGroup = self.productGroup  # Default product group
        supplierserial = self.sup_serial_number
        lowerlevelID = self.lowerlevelID  # Default lower level ID
        tests = self.tests  # Default tests
        errors = self.errors  # Default errors
        result = self.result  # Default result, e.g., "Passed"

        #Jasper data - NA
        Japer_time = datetime.datetime.now()
        formatted_ts = Japer_time.strftime('%Y-%m-%d %H:%M:%S%f')[:-3]
        date_part, time_part = formatted_ts.split()
        time_final = time_part[:-3]
        random_number = random.randint(1, 999)
        #Jasper data - NA

        # Create TestFile1 object
        TestFile1 = root(
            ts, tester, testdesc, testjig, deviceid, prefix, jobnr, serialnr,
            procedure, productGroup, supplierserial, lowerlevelID, tests, errors, result
        )

        #Output file to Jasper Server        
        error_String = ' '.join(map(str, errors))
        Jasper_result = "Test Result: "+self.result + "\nErrors: " + error_String        
        body_as_dict = {"time": time_final, "date": date_part,  "stationID": "AZZ990310240001", "barcodeID": self.serial_entry3.get(),
                          "stationData": deviceid + "," + self.serial_entry2.get(), "operatorID": tester, "noteStr": Jasper_result, "randomNumber": random_number}
        body_as_json_string = json.dumps(body_as_dict)
        #curlPost(body_as_json_string) #OUTPUT


        #output TestFile locally and on FTP server in resultdump folder
        result_filename = f"{deviceid}_{jobnr}_{ts}_results.json"

        if self.NBP_checkbox.get():
            
            result_filepath_2 = os.getcwd() + "/Test_Result_Dump_New/Production/" + result_filename     
            result_ftp_folder2 = 'Stage_Zero_Test_Results_New'
            outputJSON(TestFile1,result_filepath_2,result_filename, result_ftp_folder2) # OUTPUT
            

        if self.RMA_checkbox.get():
            
            result_filepath = os.getcwd() + "/Test_Result_Dump_New/RMA/" + result_filename     
            result_ftp_folder = 'BMS_Test_Station_New/resultdump/RMA'
            outputJSON(TestFile1,result_filepath,result_filename, result_ftp_folder) # OUTPUT

       
    def setup_sidebar(self):
        # Title
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="BMS Test Station",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.pack(pady=20, padx=20)

        # Add lock button and operator info
        self.auth_frame = ctk.CTkFrame(self.sidebar)
        self.auth_frame.pack(pady=10, fill="x", padx=20)
        
        self.lock_button = ctk.CTkButton(
            self.auth_frame,
            text="",
            width=20,
            height=20,
            fg_color="red",  # Start with red (logged out)
            hover=False,
            command=self.toggle_login
        )
        self.lock_button.pack(side="left", padx=5)
        
        self.operator_label = ctk.CTkLabel(
            self.auth_frame,
            text="Not logged in",
            font=ctk.CTkFont(size=12)
        )
        self.operator_label.pack(side="left", padx=5, fill="x", expand=True)

        # Status indicator
        self.status_frame = ctk.CTkFrame(self.sidebar)
        self.status_frame.pack(pady=20, fill="x", padx=20)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Status:",
            font=ctk.CTkFont(size=14)
        )
        self.status_label.pack(side="left", padx=5)
        
        self.status_indicator = ctk.CTkLabel(
            self.status_frame,
            text="Not logged in",
            font=ctk.CTkFont(size=14),
            text_color="yellow"
        )
        self.status_indicator.pack(side="left", padx=5)

        #Inspection Lable
        self.serial_label_BATP = ctk.CTkLabel(
            self.sidebar,
            text="Pre-ATP Inspection:",
            font=ctk.CTkFont(size=14)
        )
        self.serial_label_BATP.pack(pady=5, padx=20)
        #self.logo_label.pack(pady=20, padx=20)

        #Inspection Tickbox
        self.inspection_checkbox = ctk.CTkCheckBox(
            self.sidebar,
            text="Battery Inspection Completed",
            #state="normal",  # Ensure it is enabled
            state="disabled",
            command=self.on_checkbox_change,
        )
        self.inspection_checkbox.pack(pady=5)

        #Battery Type Lable
        self.serial_label_BT = ctk.CTkLabel(
            self.sidebar,
            text="Battery Type:",
            font=ctk.CTkFont(size=14)
        )
        self.serial_label_BT.pack(pady=10, padx=20)

        #Production Battery Tickbox
        self.NBP_checkbox = ctk.CTkCheckBox(
            self.sidebar,
            text="Production Battery Pack",
            #state="normal",  # Ensure it is enabled
            state="disabled",
            command=self.on_NBPcheckbox_change,
        )
        #self.NBP_checkbox.grid(row=1, column=0, padx=20, pady=20)
        self.NBP_checkbox.pack(pady=5)

        #RMA Battery Tickbox
        self.RMA_checkbox = ctk.CTkCheckBox(
            self.sidebar,
            text="RMA Battery Pack",
            #state="normal",  # Ensure it is enabled
            state="disabled",
            command=self.on_RMAcheckbox_change,
        )
        self.RMA_checkbox.pack(pady=20)
        
        
        # Serial number 1 input
        self.serial_label = ctk.CTkLabel(
            self.sidebar,
            text="405 Device Serial Number:",
            font=ctk.CTkFont(size=14)
        )
        self.serial_label.pack(pady=(20,5))
        
        self.serial_entry = ctk.CTkEntry(
            self.sidebar,
            placeholder_text="SZS:SZ-R48S-XXXXXXX / SC:405-XXXXXXX / JN:MFXXXXXX",
            width=400
        )
        self.serial_entry.pack(pady=(0,20))

        # Serial number 2 input
        self.serial_label2 = ctk.CTkLabel(
            self.sidebar,
            text="62 Sub-Assembly Serial Number:",
            font=ctk.CTkFont(size=14)
        )
        self.serial_label2.pack(pady=(20,5))
        
        self.serial_entry2 = ctk.CTkEntry(
            self.sidebar,
            placeholder_text="SZS:SZ-VSA-XXXXXXX / SC:62-XXXXXXX / JN:MFXXXXXX",
            width=400
        )
        self.serial_entry2.pack(pady=(0,20))
        # Serial number 2 input

        # Serial number 3 input (Track and Trace)
        self.serial_label3 = ctk.CTkLabel(
            self.sidebar,
            text="Track and Trace Serial Number:",
            font=ctk.CTkFont(size=14)
        )
        self.serial_label3.pack(pady=(20,5))
        
        self.serial_entry3 = ctk.CTkEntry(
            self.sidebar,
            placeholder_text="AXXxxxxxxxxxxxx",
            width=400
        )
        self.serial_entry3.pack(pady=(0,20))
        # Serial number 3 input (Track and Trace)

        # Buttons
        self.start_button = ctk.CTkButton(
            self.sidebar,
            text="Start Test",
            command=self.start_test,
            width=200,
            height=40,
            state="disabled"  # Start disabled
        )
        self.start_button.pack(pady=15)
        
        self.reset_button = ctk.CTkButton(
            self.sidebar,
            text="Reset",
            command=self.reset_gui,
            width=200,
            height=40,
            fg_color="transparent",
            border_width=2,
            state="disabled"  # Start disabled
        )
        self.reset_button.pack(pady=15)      
     
    def on_NBPcheckbox_change(self):
        if self.NBP_checkbox.get():
            #print("Checkbox is checked")
            pass
        else:
            #print("Checkbox is unchecked")
            pass

    def on_RMAcheckbox_change(self):
        if self.RMA_checkbox.get():
            print("RMA Checkbox is checked")
            #self.serial_entry2.configure(state="disabled", bg="grey")  # Grey out and disable
            self.serial_entry2.delete(0, 'end')  # Clear content
            self.serial_entry2.insert(0,"No Sub Assem Serial Number for RMA packs")
            self.serial_entry2.configure(state="disabled")  # Grey out and disable
            self.serial_entry3.delete(0, 'end')
            self.serial_entry3.insert(0,"No Track and Trace for RMA packs")
            self.serial_entry3.configure(state="disabled")  # Grey out and disable
            pass
        else:
            print("RMA Checkbox is unchecked")
            self.serial_entry2.configure(state="normal")  # Enable and reset background
            self.serial_entry2.delete(0, 'end')  # Clear content
            self.serial_entry3.configure(state="normal")  # Enable and reset background
            self.serial_entry3.delete(0, 'end')  # Clear content
            pass


    def on_checkbox_change(self):
        if self.inspection_checkbox.get():
            #print("Checkbox is checked")
            pass
        else:
            #print("Checkbox is unchecked")
            pass
            

    def setup_main_content(self):
        # Configure main content grid
        self.main_content.grid_columnconfigure(0, weight=1)
        
        # Results display
        self.result_text = ctk.CTkTextbox(
            self.main_content,
            width=800,
            height=700,
            font=ctk.CTkFont(size=12)
        )
        self.result_text.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    def start_test(self):

        if not self.inspection_checkbox.get():  # If checkbox is not ticked
            CTkMessagebox(
                title="Inspection Not Completed", 
                message="Please confirm that the Battey Packs Visual and Safety Inspection has been Completed",
                icon="warning"
            )
            return  # Don't proceed with the test

        if not (self.RMA_checkbox.get() or self.NBP_checkbox.get()):
            CTkMessagebox(
                title="Type of Battery Pack Not indicated", 
                message="Please select if it is a New Battery Pack or a Returned RMA Battery Pack which will be tested",
                icon="warning"
            )
            return  # Don't proceed with the test

        if (self.RMA_checkbox.get() and self.NBP_checkbox.get()):
            CTkMessagebox(
                title="Type Both Battery Packs Selected", 
                message="Please select if it is a New Battery Pack OR a Returned RMA Battery Pack which will be tested. You Cannot Select Both Options",
                icon="warning"
            )
            return  # Don't proceed with the test


        if not self.current_operator:
            CTkMessagebox(
                title="Access Denied",
                message="Please log in before starting a test",
                icon="warning"
            )
            self.show_login_dialog()
            return

        ini_serial_number_405 = (self.serial_entry.get().replace(" ", "")) 
        serial_number_405 = ini_serial_number_405.replace("/", " | ")
        #print(f"405 Serial Number: {serial_number_405}")

        ini_temp_serial_number_405 = (self.serial_entry.get().replace(" ", ""))    
        temp_serial_number_405 = (ini_temp_serial_number_405.replace("/", " / "))
        #print(f"Temp 405 Serial Number: {temp_serial_number_405}")

        
        ini_serial_number_VSA = (self.serial_entry2.get().replace(" ", "")) 
        serial_number_VSA = (ini_serial_number_VSA.replace("/", " | ")) 

        #print(f"VSA Serial Number: {serial_number_VSA}")

        ini_temp_serial_number_VSA = (self.serial_entry2.get().replace(" ", "")) 
        temp_serial_number_VSA = (ini_temp_serial_number_VSA.replace("/", " / ")) 
        #print(f"Temp VSA Serial Number: {temp_serial_number_VSA}")

        Tnt_serial_number = self.serial_entry3.get()
        self.serialnr =  temp_serial_number_405

        #if (self.RMA_checkbox.get() and self.NBP_checkbox.get()):

        #new battery Pack
        if self.NBP_checkbox.get():

            if ((maskCheck(temp_serial_number_405, "R48S") == True) or (maskCheck(temp_serial_number_405, "R48") == True) or 
                (maskCheck(temp_serial_number_405, "V48") == True) or (maskCheck(temp_serial_number_405, "H48") == True) or (maskCheck(temp_serial_number_405, "B48S") == True) or (maskCheck(temp_serial_number_405, "SRG") == True) or (maskCheck(temp_serial_number_405, "GR5") == True)):
                parts = serial_number_405.split(" | ")
            else:
                CTkMessagebox(title="Error", message="Please enter the correct 405 serial number", icon="warning") 
                self.serial_entry.delete(0, "end")            
                return           

            if ((maskCheck(temp_serial_number_VSA, "VSA") == True) or (maskCheck(temp_serial_number_VSA, "C48") == True) or (maskCheck(temp_serial_number_VSA, "C48S") == True) or (maskCheck(temp_serial_number_VSA, "HSA") == True) or (maskCheck(temp_serial_number_VSA, "GR5S") == True) or (maskCheck(temp_serial_number_VSA, "GRBA") == True)):
                parts_VSA = serial_number_VSA.split(" | ")
                #parts_VSA = serial_number_VSA.split(" | ")
            else:
                CTkMessagebox(title="Error", message="Please enter the correct VSA/HSA/C48 serial number", icon="warning") 
                self.serial_entry2.delete(0, "end")
                return  
            
            if ((maskCheck(Tnt_serial_number, "TnT") == True) or (maskCheck(Tnt_serial_number, "TnT2") == True)):
                pass
            else:
                CTkMessagebox(title="Error", message="Please enter the correct Track and Trace serial number", icon="warning") 
                self.serial_entry3.delete(0, "end")
                return

            self.lowerlevelID = parts_VSA[0].split(":")[1]

        #RMA Battery Pack    
        if self.RMA_checkbox.get():

            if ((maskCheck(temp_serial_number_405, "R48S") == True) or (maskCheck(temp_serial_number_405, "R48") == True) or 
                (maskCheck(temp_serial_number_405, "V48") == True) or (maskCheck(temp_serial_number_405, "H48") == True) or (maskCheck(temp_serial_number_405, "B48S") == True)  or (maskCheck(temp_serial_number_405, "SRG") == True) or (maskCheck(temp_serial_number_405, "GR5") == True)):
                parts = serial_number_405.split(" | ")
            else:
                CTkMessagebox(title="Error", message="Please enter the correct 405 serial number", icon="warning") 
                self.serial_entry.delete(0, "end")            
                return           

            self.lowerlevelID = "RMA_Pack"  

        try:

            self.reset_button.configure(state="normal")
            self.status_indicator.configure(text="Testing...", text_color="yellow")
            self.update()

            pack_info = self.run_test(serial_number_405)

            if pack_info:

                self.sup_serial_number = pack_info['Acquire Device Manufacture Info'].get('BMS Serial Number', 'Unknown Device')
                self.display_results(pack_info)
                errors = self.validate_results(pack_info)
                self.errors = errors
                self.device_id = parts[0].split(":")[1] 
                self.prefix = self.device_id.split("-")[1]  
                print("Prefix\n") 
                print(self.prefix)    
                self.SC = parts[1]             
                self.jobnr = parts[2]
                self.tests = []
                filepath2 = os.path.join("data", 'pack_info.json') #works


                # Update status and enable the reset button after the test
                if not errors:
                    self.status_indicator.configure(text="PASS", text_color="green")
                    CTkMessagebox(title="Success", message="Test passed successfully!", icon="check")
                    self.result = "Pass"
                    self.errors = "No Errors"
                    #send_test_data(self.prefix, "Passed")
                else:
                    self.status_indicator.configure(text="FAIL", text_color="red")
                    self.result = "Fail"
                    #send_test_data(self.prefix, "Failed")
                    
                    # Create a custom CTkToplevel window for displaying errors
                    error_window = ctk.CTkToplevel(self)
                    error_window.title("Test Failed")
                    error_window.geometry("500x450")  # Adjust size as needed
                    error_window.resizable(True, True)

                    # Add a label for the title
                    error_label = ctk.CTkLabel(
                        error_window,
                        text="Test failed with the following errors:",
                        font=ctk.CTkFont(size=14, weight="bold"),
                        wraplength=480
                    )
                    error_label.pack(pady=10, padx=10)

                    # Add a scrollable textbox for errors
                    error_textbox = ctk.CTkTextbox(
                        error_window,
                        width=480,
                        height=300,
                        font=ctk.CTkFont(size=12)
                    )
                    error_textbox.pack(pady=10, padx=10, fill="both", expand=True)

                    # Insert errors into the textbox
                    error_textbox.insert("1.0", "\n".join(errors))
                    error_textbox.configure(state="disabled")  # Make it read-only

                    # Add a close button
                    close_button = ctk.CTkButton(
                        error_window,
                        text="OK",
                        command=error_window.destroy
                    )
                    close_button.pack(pady=10)
                    
                #New Battery Packs
                ###############################################################################################

                if self.NBP_checkbox.get():
                    config_pia =self.config["PIA"]
                    config_device = self.config["Acquire Device Manufacture Info"]
                    config_alarms = self.config["Alarms"]
                    config_func_switch = self.config["Function Switch Param"]
                    config_basic_params = self.config["Basic Param"]

                if self.RMA_checkbox.get():
                    config_pia =self.configRMA["PIA"]
                    config_device = self.configRMA["Acquire Device Manufacture Info"]
                    config_alarms = self.configRMA["Alarms"]
                    config_func_switch = self.configRMA["Function Switch Param"]
                    config_basic_params = self.configRMA["Basic Param"]

                pack_data = BMSTestApp.load_pack_info(filepath2)
                Device_info = pack_data.get('Acquire Device Manufacture Info')
                PIA_info = pack_data.get('PIA')
                Alarms_info = pack_data.get('Alarms')
                Function_Switch_info = pack_data.get('Function Switch Param')
                Basic_Param_info = pack_data.get('Basic Param')
            
                #Test Data for Firmware Version
                if float(config_device["Firmware Version"]) == float(Device_info["Firmware Version"]):
                    device_result = "PASS"
                else:
                    device_result = "FAIL"
                
                firm_test = test(list(config_device.keys())[2],
                                    ((config_device["Firmware Version"])),
                                    (Device_info["Firmware Version"]), device_result, "Firmware Version Check", "NA","NA")
                

                #Test Data for Pack Voltage
                if config_pia["Pack Voltage"][0] <= PIA_info["Pack Voltage"] <= config_pia["Pack Voltage"][1]:
                    pack_result = "PASS"
                else:
                    pack_result = "FAIL"

                pack_test = test(next(iter(config_pia)),
                                    (config_pia["Pack Voltage"][0]+config_pia["Pack Voltage"][1])/2,
                                    PIA_info["Pack Voltage"], pack_result, "Pack Voltage Test", str(config_pia["Pack Voltage"]),"NA")
                
                                            
                #Test Data for Current
                if config_pia["Current"] >= PIA_info["Current"]:
                    current_result = "PASS"
                else:
                    current_result = "FAIL"

                current_test = test(list(config_pia.keys())[1],
                                    (config_pia["Current"]),
                                    PIA_info["Current"], current_result, "Current Test", "NA","NA")                                             
              
                #Test Data for SOC               
                if config_pia["SOC"][0] <= PIA_info["SOC"] <= config_pia["SOC"][1]:
                    soc_result = "PASS"
                else:
                    soc_result = "FAIL"

                soc_test = test(list(config_pia.keys())[5],
                                    (config_pia["SOC"][0]+config_pia["SOC"][1])/2,
                                    PIA_info["SOC"], soc_result, "SOC", str(config_pia["SOC"]),"NA")
                
                #Test Data for SOH                  
                if config_pia["SOH"][0] <= PIA_info["SOH"] <= config_pia["SOH"][1]:
                    soh_result = "PASS"
                else:
                    soc_result = "FAIL"

                soh_test = test(list(config_pia.keys())[6],
                                    (config_pia["SOH"][0]+config_pia["SOH"][1])/2,
                                    PIA_info["SOH"], soh_result, "SOH", str(config_pia["SOH"]),"NA")           

                #Alarms data check
                # if (config_alarms["Voltage Alarms 1"] == Alarms_info["Voltage Alarms 1"] and
                #     config_alarms["Temperature Alarms"] == Alarms_info["Temperature Alarms"] and 
                #     config_alarms["Environment Alarms"] == Alarms_info["Environment Alarms"] and
                #     (config_alarms["Voltage Alarms 2"][0] == Alarms_info["Voltage Alarms 2"] or config_alarms["Voltage Alarms 2"][1] == Alarms_info["Voltage Alarms 2"]) and
                #     config_alarms["Current Alarms 1"] == Alarms_info["Current Alarms 1"] and
                #     (config_alarms["Current Alarms 2"][0] == Alarms_info["Current Alarms 2"] or config_alarms["Current Alarms 2"][1] == Alarms_info["Current Alarms 2"]) and
                #     config_alarms["Capacity and other Alarms"] == Alarms_info["Capacity and other Alarms"] and
                #     config_alarms["Equalization Alarms"] == Alarms_info["Equalization Alarms"] and
                #     (config_alarms["Indicator Alarms"][0] == Alarms_info["Indicator Alarms"] or config_alarms["Indicator Alarms"][1] == Alarms_info["Indicator Alarms"]) and
                #     config_alarms["Hard fault Alarms"] == Alarms_info["Hard fault Alarms"]):

                #     alarms_result = "PASS" 
                # else:
                #     alarms_result = "FAIL"
                
                # alarms_test = test("Alarms","NA",
                #                     "NA", alarms_result, "Alarms Check", "NA","NA") 


                #Function Switch Parameters
                if (
                    config_func_switch["Cell high voltage alarm"] == Function_Switch_info["Cell high voltage alarm"] and
                    config_func_switch["Cell over voltage protection"] == Function_Switch_info["Cell over voltage protection"] and
                    config_func_switch["Cell low voltage alarm"] == Function_Switch_info["Cell low voltage alarm"] and
                    config_func_switch["Cell under voltage protection"] == Function_Switch_info["Cell under voltage protection"] and
                    config_func_switch["Battery high voltage alarm"] == Function_Switch_info["Battery high voltage alarm"] and
                    config_func_switch["Battery over voltage protection"] == Function_Switch_info["Battery over voltage protection"] and
                    config_func_switch["Battery low voltage alarm"] == Function_Switch_info["Battery low voltage alarm"] and
                    config_func_switch["Battery under voltage protection"] == Function_Switch_info["Battery under voltage protection"] and
                    config_func_switch["Charge high temperature alarm"] == Function_Switch_info["Charge high temperature alarm"] and
                    config_func_switch["Charge over temperature protection"] == Function_Switch_info["Charge over temperature protection"] and
                    config_func_switch["Charge low temperature alarm"] == Function_Switch_info["Charge low temperature alarm"] and
                    config_func_switch["Charge under temperature protection"] == Function_Switch_info["Charge under temperature protection"] and
                    config_func_switch["Discharge high temperature alarm"] == Function_Switch_info["Discharge high temperature alarm"] and
                    config_func_switch["Discharge over temperature protection"] == Function_Switch_info["Discharge over temperature protection"] and
                    config_func_switch["Discharge low temperature alarm"] == Function_Switch_info["Discharge low temperature alarm"] and
                    config_func_switch["Discharge under temperature protection"] == Function_Switch_info["Discharge under temperature protection"] and
                    config_func_switch["High ambient temperature alarm"] == Function_Switch_info["High ambient temperature alarm"] and
                    config_func_switch["Over ambient temperature protection"] == Function_Switch_info["Over ambient temperature protection"] and
                    config_func_switch["Low ambient temperature alarm"] == Function_Switch_info["Low ambient temperature alarm"] and
                    config_func_switch["Under ambient temperature protection"] == Function_Switch_info["Under ambient temperature protection"] and
                    config_func_switch["Power high temperature alarm"] == Function_Switch_info["Power high temperature alarm"] and
                    config_func_switch["Power over temperature protection"] == Function_Switch_info["Power over temperature protection"] and
                    config_func_switch["Cell temperature low heating"] == Function_Switch_info["Cell temperature low heating"] and
                    config_func_switch["Cell voltage Fault (Reserved)"] == Function_Switch_info["Cell voltage Fault (Reserved)"] and
                    (config_func_switch["Focs Output"][0] == Function_Switch_info["Focs Output"] or config_func_switch["Focs Output"][1] == Function_Switch_info["Focs Output"]) and
                    config_func_switch["Heat dissipation turned on"] == Function_Switch_info["Heat dissipation turned on"] and
                    config_func_switch["CapLeds idle display"] == Function_Switch_info["CapLeds idle display"] and
                    config_func_switch["Reserved 1 (Voltage Alarms 2)"] == Function_Switch_info["Reserved 1 (Voltage Alarms 2)"] and
                    config_func_switch["Reserved 2 (Voltage Alarms 2)"] == Function_Switch_info["Reserved 2 (Voltage Alarms 2)"] and
                    config_func_switch["Reserved 3 (Voltage Alarms 2)"] == Function_Switch_info["Reserved 3 (Voltage Alarms 2)"] and
                    config_func_switch["Reserved 4 (Voltage Alarms 2)"] == Function_Switch_info["Reserved 4 (Voltage Alarms 2)"] and
                    config_func_switch["Reserved 5 (Voltage Alarms 2)"] == Function_Switch_info["Reserved 5 (Voltage Alarms 2)"] and
                    config_func_switch["Charge current alarm"] == Function_Switch_info["Charge current alarm"] and
                    config_func_switch["Charge over current protection"] == Function_Switch_info["Charge over current protection"] and
                    config_func_switch["Secondary charge over current protection"] == Function_Switch_info["Secondary charge over current protection"] and
                    config_func_switch["Discharge current alarm"] == Function_Switch_info["Discharge current alarm"] and
                    config_func_switch["Discharge over current protection"] == Function_Switch_info["Discharge over current protection"] and
                    config_func_switch["Secondary discharge over current protection"] == Function_Switch_info["Secondary discharge over current protection"] and
                    config_func_switch["Output short-circuit protection"] == Function_Switch_info["Output short-circuit protection"] and
                    config_func_switch["Reserved 6 (Current Alarms 1)"] == Function_Switch_info["Reserved 6 (Current Alarms 1)"] and
                    config_func_switch["Output short-circuit lock"] == Function_Switch_info["Output short-circuit lock"] and
                    (config_func_switch["Reserved 7 (Current Alarms 2)"][0] == Function_Switch_info["Reserved 7 (Current Alarms 2)"] or config_func_switch["Reserved 7 (Current Alarms 2)"][1] == Function_Switch_info["Reserved 7 (Current Alarms 2)"]) and
                    config_func_switch["Secondary charge over current lock"] == Function_Switch_info["Secondary charge over current lock"] and
                    config_func_switch["Secondary discharge over current lock"] == Function_Switch_info["Secondary discharge over current lock"] and
                    config_func_switch["Reserved 8 (Current Alarms 2)"] == Function_Switch_info["Reserved 8 (Current Alarms 2)"] and
                    config_func_switch["Reserved 9 (Current Alarms 2)"] == Function_Switch_info["Reserved 9 (Current Alarms 2)"] and
                    config_func_switch["Reserved 10 (Current Alarms 2)"] == Function_Switch_info["Reserved 10 (Current Alarms 2)"] and
                    config_func_switch["Reserved 11 (Current Alarms 2)"] == Function_Switch_info["Reserved 11 (Current Alarms 2)"] and
                    config_func_switch["Low SOC alarm"] == Function_Switch_info["Low SOC alarm"] and
                    config_func_switch["Intermittent charge"] == Function_Switch_info["Intermittent charge"] and
                    config_func_switch["External switch control"] == Function_Switch_info["External switch control"] and
                    config_func_switch["Static stand-by sleep"] == Function_Switch_info["Static stand-by sleep"] and
                    config_func_switch["History data recording"] == Function_Switch_info["History data recording"] and
                    config_func_switch["Under SOC protect"] == Function_Switch_info["Under SOC protect"] and
                    config_func_switch["Active-limited current"] == Function_Switch_info["Active-limited current"] and
                    config_func_switch["Passive-limited current"] == Function_Switch_info["Passive-limited current"] and
                    config_func_switch["Equilibrium module to open"] == Function_Switch_info["Equilibrium module to open"] and
                    config_func_switch["Static equilibrium indicate"] == Function_Switch_info["Static equilibrium indicate"] and
                    config_func_switch["Static equilibrium overtime"] == Function_Switch_info["Static equilibrium overtime"] and
                    config_func_switch["Equalization temperature limit"] == Function_Switch_info["Equalization temperature limit"] and
                    config_func_switch["Reserved 12 (Equalization Alarms)"] == Function_Switch_info["Reserved 12 (Equalization Alarms)"] and
                    config_func_switch["Reserved 13 (Equalization Alarms)"] == Function_Switch_info["Reserved 13 (Equalization Alarms)"] and
                    config_func_switch["Reserved 14 (Equalization Alarms)"] == Function_Switch_info["Reserved 14 (Equalization Alarms)"] and
                    config_func_switch["Reserved 15 (Equalization Alarms)"] == Function_Switch_info["Reserved 15 (Equalization Alarms)"] and
                    (config_func_switch["Buzzer indicator"][0] == Function_Switch_info["Buzzer indicator"] or config_func_switch["Buzzer indicator"][1] == Function_Switch_info["Buzzer indicator"]) and
                    config_func_switch["LCD display"] == Function_Switch_info["LCD display"] and
                    config_func_switch["Manual forced output"] == Function_Switch_info["Manual forced output"] and
                    config_func_switch["Auto forced output"] == Function_Switch_info["Auto forced output"] and
                    config_func_switch["Empty (Indicator Alarms)"] == Function_Switch_info["Empty (Indicator Alarms)"] and
                    config_func_switch["Aerosol detection function"] == Function_Switch_info["Aerosol detection function"] and
                    config_func_switch["Aerosol normally disconnected mode"] == Function_Switch_info["Aerosol normally disconnected mode"] and
                    config_func_switch["Current detector temperature compensation"] == Function_Switch_info["Current detector temperature compensation"] and
                    config_func_switch["NTC failure"] == Function_Switch_info["NTC failure"] and
                    config_func_switch["AFE failure"] == Function_Switch_info["AFE failure"] and
                    config_func_switch["Charge mosfets failure"] == Function_Switch_info["Charge mosfets failure"] and
                    config_func_switch["Discharge mosfets failure"] == Function_Switch_info["Discharge mosfets failure"] and
                    config_func_switch["Cell diff failure"] == Function_Switch_info["Cell diff failure"] and
                    config_func_switch["Cell break"] == Function_Switch_info["Cell break"] and
                    config_func_switch["Key failure"] == Function_Switch_info["Key failure"] and
                    config_func_switch["Aerosol Alarm"] == Function_Switch_info["Aerosol Alarm"]
                ):
                    func_switch_result = "PASS"
                else:
                    func_switch_result = "FAIL"

                func_switch_test = test("Function Switch", "NA", "NA", (func_switch_result), "Function Switch Param Check", "NA", "NA")


                # Basic Parameters
                if(
                    config_basic_params["Ntc Number"] == Basic_Param_info["Ntc Number"] and
                    config_basic_params["Cell Serial Battery Number"] == Basic_Param_info["Cell Serial Battery Number"] and
                    config_basic_params["Battery High Voltage Recovery(V)"] == Basic_Param_info["Battery High Voltage Recovery(V)"] and
                    config_basic_params["Battery High Voltage Alarm(V)"] == Basic_Param_info["Battery High Voltage Alarm(V)"] and
                    config_basic_params["Battery Over Voltage Recovery(V)"] == Basic_Param_info["Battery Over Voltage Recovery(V)"] and
                    config_basic_params["Battery Over Voltage Protection(V)"] == Basic_Param_info["Battery Over Voltage Protection(V)"] and
                    config_basic_params["Battery Low Voltage Recovery(V)"] == Basic_Param_info["Battery Low Voltage Recovery(V)"] and
                    config_basic_params["Battery Low Voltage Alarm(V)"] == Basic_Param_info["Battery Low Voltage Alarm(V)"] and
                    config_basic_params["Battery Under Voltage Recovery(V)"] == Basic_Param_info["Battery Under Voltage Recovery(V)"] and
                    config_basic_params["Battery Under Voltage Protection(V)"] == Basic_Param_info["Battery Under Voltage Protection(V)"] and
                    config_basic_params["Cell High Voltage Recovery(V)"] == Basic_Param_info["Cell High Voltage Recovery(V)"] and
                    config_basic_params["Cell High Voltage Alarm(V)"] == Basic_Param_info["Cell High Voltage Alarm(V)"] and
                    config_basic_params["Cell Over Voltage Recovery(V)"] == Basic_Param_info["Cell Over Voltage Recovery(V)"] and
                    config_basic_params["Cell Over Voltage Protection(V)"] == Basic_Param_info["Cell Over Voltage Protection(V)"] and
                    config_basic_params["Cell Low Voltage Recovery(V)"] == Basic_Param_info["Cell Low Voltage Recovery(V)"] and
                    config_basic_params["Cell Low Voltage Alarm(V)"] == Basic_Param_info["Cell Low Voltage Alarm(V)"] and
                    config_basic_params["Cell Under Voltage Recovery(V)"] == Basic_Param_info["Cell Under Voltage Recovery(V)"] and
                    config_basic_params["Cell Under Voltage Protection(V)"] == Basic_Param_info["Cell Under Voltage Protection(V)"] and
                    config_basic_params["Cell Under Voltage Fault(V)"] == Basic_Param_info["Cell Under Voltage Fault(V)"] and
                    #config_basic_params["Cell Diff Protection(V)"] == Basic_Param_info["Cell Diff Protection(V)"] and
                    #config_basic_params["Secondary Charge Current Protection(V)"] == Basic_Param_info["Secondary Charge Current Protection(V)"] and
                    config_basic_params["Charge High Current Recover(A)"] == Basic_Param_info["Charge High Current Recover(A)"] and
                    config_basic_params["Charge High Current Alarm(A)"] == Basic_Param_info["Charge High Current Alarm(A)"] and
                    config_basic_params["Charge Over Current Protection(A)"] == Basic_Param_info["Charge Over Current Protection(A)"] and
                    config_basic_params["Charge Over Current Time Delay(s)"] == Basic_Param_info["Charge Over Current Time Delay(s)"] and
                    config_basic_params["Secondary Charge Current Protection 2 (A)"] == Basic_Param_info["Secondary Charge Current Protection 2 (A)"] and
                    config_basic_params["Secondary Charge Current Time Delay (ms)"] == Basic_Param_info["Secondary Charge Current Time Delay (ms)"] and
                    config_basic_params["Discharge Low Current Recover(A)"] == Basic_Param_info["Discharge Low Current Recover(A)"] and
                    config_basic_params["Discharge Low Current Alarm(A)"] == Basic_Param_info["Discharge Low Current Alarm(A)"] and
                    config_basic_params["Discharge Over Current Protection(A)"] == Basic_Param_info["Discharge Over Current Protection(A)"] and
                    config_basic_params["Discharge Over Current Time Delay(s)"] == Basic_Param_info["Discharge Over Current Time Delay(s)"] and
                    config_basic_params["Secondary Discharge Current Protection(A)"] == Basic_Param_info["Secondary Discharge Current Protection(A)"] and
                    config_basic_params["Secondary Discharge Current Time Delay(ms)"] == Basic_Param_info["Secondary Discharge Current Time Delay(ms)"] and
                    config_basic_params["Over Current Recover Time Delay(s)"] == Basic_Param_info["Over Current Recover Time Delay(s)"] and
                    config_basic_params["Over Current Lock Times"] == Basic_Param_info["Over Current Lock Times"] and
                    config_basic_params["Charge High Switch Limited Time(s)"] == Basic_Param_info["Charge High Switch Limited Time(s)"] and
                    #config_basic_params["Pulse CurrentA"] == Basic_Param_info["Pulse CurrentA"] and
                    config_basic_params["Pulse Time(s)"] == Basic_Param_info["Pulse Time(s)"] and
                    config_basic_params["Normal precharge completion rate(%)"] == Basic_Param_info["Normal precharge completion rate(%)"] and
                    config_basic_params["Abnormal precharge completion rate(%)"] == Basic_Param_info["Abnormal precharge completion rate(%)"] and
                    config_basic_params["Precharge over time(s)"] == Basic_Param_info["Precharge over time(s)"] and
                    config_basic_params["Charge High Temperature Recover(C)"] == Basic_Param_info["Charge High Temperature Recover(C)"] and
                    config_basic_params["Charge High Temperature Alarm(C)"] == Basic_Param_info["Charge High Temperature Alarm(C)"] and
                    config_basic_params["Charge Over Temperature Recover(C)"] == Basic_Param_info["Charge Over Temperature Recover(C)"] and
                    config_basic_params["Charge Over Temperature Protection(C)"] == Basic_Param_info["Charge Over Temperature Protection(C)"] and
                    config_basic_params["Charge Low Temperature Recover(C)"] == Basic_Param_info["Charge Low Temperature Recover(C)"] and
                    config_basic_params["Charge Low Temperature Alarm(C)"] == Basic_Param_info["Charge Low Temperature Alarm(C)"] and
                    config_basic_params["Charge Under Temperature Recover(C)"] == Basic_Param_info["Charge Under Temperature Recover(C)"] and
                    config_basic_params["Charge Under Temperature Protection(C)"] == Basic_Param_info["Charge Under Temperature Protection(C)"] and
                    config_basic_params["Discharge High Temperature Recover(C)"] == Basic_Param_info["Discharge High Temperature Recover(C)"] and
                    config_basic_params["Discharge High Temperature Alarm(C)"] == Basic_Param_info["Discharge High Temperature Alarm(C)"] and
                    config_basic_params["Discharge Over Temperature Recover(C)"] == Basic_Param_info["Discharge Over Temperature Recover(C)"] and
                    config_basic_params["Discharge Over Temperature Protection(C)"] == Basic_Param_info["Discharge Over Temperature Protection(C)"] and
                    config_basic_params["Discharge Low Temperature Recover(C)"] == Basic_Param_info["Discharge Low Temperature Recover(C)"] and
                    config_basic_params["Discharge Low Temperature Alarm(C)"] == Basic_Param_info["Discharge Low Temperature Alarm(C)"] and
                    config_basic_params["Discharge Under Temperature Recover(C)"] == Basic_Param_info["Discharge Under Temperature Recover(C)"] and
                    config_basic_params["Discharge Under Temperature Protection(C)"] == Basic_Param_info["Discharge Under Temperature Protection(C)"] and
                    config_basic_params["High Environment Temperature Recover(C)"] == Basic_Param_info["High Environment Temperature Recover(C)"] and
                    config_basic_params["High Environment Temperature Alarm(C)"] == Basic_Param_info["High Environment Temperature Alarm(C)"] and
                    config_basic_params["Over Environment Temperature Recover(C)"] == Basic_Param_info["Over Environment Temperature Recover(C)"] and
                    config_basic_params["Over Environment Temperature Protection(C)"] == Basic_Param_info["Over Environment Temperature Protection(C)"] and
                    config_basic_params["Low Environment Temperature Recover(C)"] == Basic_Param_info["Low Environment Temperature Recover(C)"] and
                    config_basic_params["Low Environment Temperature Alarm(C)"] == Basic_Param_info["Low Environment Temperature Alarm(C)"] and
                    config_basic_params["Under Environment Temperature Recover(C)"] == Basic_Param_info["Under Environment Temperature Recover(C)"] and
                    config_basic_params["Under Environment Temperature Protection(C)"] == Basic_Param_info["Under Environment Temperature Protection(C)"] and
                    config_basic_params["High Power Temperature Recover(C)"] == Basic_Param_info["High Power Temperature Recover(C)"] and
                    #config_basic_params["High Power Temperature Alarm(C)"] == Basic_Param_info["High Power Temperature Alarm(C)"] and
                    config_basic_params["Over Power Temperature Recover(C)"] == Basic_Param_info["Over Power Temperature Recover(C)"] and
                    config_basic_params["Over Power Temperature Protection(C)"] == Basic_Param_info["Over Power Temperature Protection(C)"] and
                    config_basic_params["Cell Heating Stop(C)"] == Basic_Param_info["Cell Heating Stop(C)"] and
                    config_basic_params["Cell Heating Open(C)"] == Basic_Param_info["Cell Heating Open(C)"] and
                    config_basic_params["Equalization High Temperature Prohibit(C)"] == Basic_Param_info["Equalization High Temperature Prohibit(C)"] and
                    config_basic_params["Equalization Low Temperature Prohibit(C)"] == Basic_Param_info["Equalization Low Temperature Prohibit(C)"] and
                    config_basic_params["Static Equilibrium Time"] == Basic_Param_info["Static Equilibrium Time"] and
                    config_basic_params["Equalization Open Voltage(mV)"] == Basic_Param_info["Equalization Open Voltage(mV)"] and
                    config_basic_params["Equalization Open Voltage Difference(mV)"] == Basic_Param_info["Equalization Open Voltage Difference(mV)"] and
                    config_basic_params["Equalization Stop Voltage Difference(mV)"] == Basic_Param_info["Equalization Stop Voltage Difference(mV)"] and
                    config_basic_params["SOC Full Release(%)"] == Basic_Param_info["SOC Full Release(%)"] and
                    config_basic_params["SOC Low Recover(%)"] == Basic_Param_info["SOC Low Recover(%)"] and
                    config_basic_params["SOC Low Alarm(%)"] == Basic_Param_info["SOC Low Alarm(%)"] and
                    config_basic_params["SOC Under Recover(%)"] == Basic_Param_info["SOC Under Recover(%)"] and
                    config_basic_params["SOC Under Protection(%)"] == Basic_Param_info["SOC Under Protection(%)"] and
                    config_basic_params["Battery Rated Capacity(Ah)"] == Basic_Param_info["Battery Rated Capacity(Ah)"] and                  
                    (config_basic_params["Battery Total Capacity(Ah)"][0] <= Basic_Param_info["Battery Total Capacity(Ah)"] <= config_basic_params["Battery Total Capacity(Ah)"][1]) and
                    (config_basic_params["Residual Capacity(Ah)"][0] <= Basic_Param_info["Residual Capacity(Ah)"] <= config_basic_params["Battery Total Capacity(Ah)"][1]) and
                    config_basic_params["Stand-by to Sleep Time(s)"] == Basic_Param_info["Stand-by to Sleep Time(s)"] and
                    config_basic_params["Focs Output Delay Time(s)"] == Basic_Param_info["Focs Output Delay Time(s)"] and
                    config_basic_params["Focs Output Split(Min)"] == Basic_Param_info["Focs Output Split(Min)"] and
                    config_basic_params["Pcs Output Timers(s)"] == Basic_Param_info["Pcs Output Timers(s)"] and
                    config_basic_params["Compensating Position 1(Cell)"] == Basic_Param_info["Compensating Position 1(Cell)"] and
                    config_basic_params["Position 1 Resistance (mOhm)"] == Basic_Param_info["Position 1 Resistance (mOhm)"] and
                    config_basic_params["Compensating Position 2(Cell)"] == Basic_Param_info["Compensating Position 2(Cell)"] and
                    config_basic_params["Position 2 Resistance(mOhm)"] == Basic_Param_info["Position 2 Resistance(mOhm)"] and
                    config_basic_params["Cell Diff Alarm(mV)"] == Basic_Param_info["Cell Diff Alarm(mV)"] and
                    config_basic_params["Diff Alarm Recover(mV)"] == Basic_Param_info["Diff Alarm Recover(mV)"] and
                    config_basic_params["PCS Request Charge Limit Voltage(V)"] == Basic_Param_info["PCS Request Charge Limit Voltage(V)"] and
                    config_basic_params["PCS Request Charge Limit Current(A)"] == Basic_Param_info["PCS Request Charge Limit Current(A)"]


                ):
                    basic_params_result = "PASS"
                else:
                    basic_params_result = "FAIL"

                basic_params_test = test("Basic Parameters", "NA", "NA", (basic_params_result), "Basic Parameters Check", "NA", "NA")



                #Append test dictionaries to test object
                self.tests.append(firm_test.__dict__)
                self.tests.append(current_test.__dict__)
                self.tests.append(pack_test.__dict__)
                self.tests.append(soc_test.__dict__)
                self.tests.append(soh_test.__dict__)
                #self.tests.append(alarms_test.__dict__)
                self.tests.append(func_switch_test.__dict__)
                self.tests.append(basic_params_test.__dict__)
                self.store_test_data()

                #RMA Battery Packs
                ###############################################################################################
            

                # Enable reset button after test completion
                self.reset_button.configure(state="normal")
        except Exception as e:
            self.status_indicator.configure(text="ERROR", text_color="red")
            CTkMessagebox(title="Error", message=str(e), icon="cancel")
            # Enable reset button even on error
            self.reset_button.configure(state="normal")

    def load_test_criteria(self):
        if self.NBP_checkbox.get():
            with open('config.json', 'r') as criteria_file:
                return json.load(criteria_file)
            
        if self.RMA_checkbox.get():
            with open('configRMA.json', 'r') as criteria_file:
                return json.load(criteria_file)

    # Validate the test results against the criteria
    def validate_results(self, pack_info):
        if self.NBP_checkbox.get():
            with open('config.json', 'r') as criteria_file:
                return json.load(criteria_file)
            
        if self.RMA_checkbox.get():
            with open('configRMA.json', 'r') as criteria_file:
                return json.load(criteria_file)

    # Validate the test results against the criteria
    def validate_results(self, pack_info):
        criteria = self.load_test_criteria()
        criteria['Acquire Device Manufacture Info']['BMS Serial Number'] = pack_info['Acquire Device Manufacture Info']['BMS Serial Number']
        
        errors = []  # List to hold error messages

        # Validate PIA
        for key, value in criteria['PIA'].items():
            if key in ['Raw Response', 'BMS Serial Number']:
                continue  # Skip these fields
            if isinstance(value, list):  # Range check
                if not (value[0] <= pack_info['PIA'][key] <= value[1]):
                    errors.append(f"\nPIA - {key} out of range: {pack_info['PIA'][key]} not in {value}")
            else:  # Exact match
                if pack_info['PIA'][key] != value:
                    errors.append(f"\nPIA - {key} mismatch:\nExpected -> {value}\nReceived -> {pack_info['PIA'][key]}")

        # Validate PIC
        for key, value in criteria['PIC'].items():
            if key == 'Raw Response':  # Skip this field in PIC
                continue
            if pack_info['PIC'][key] != value:
                errors.append(f"\nPIC - {key} mismatch:\nExpected -> {value}\nReceived -> {pack_info['PIC'][key]}")

        # Validate Alarms

        # for key, expected_value in criteria['Alarms'].items():
        #     if key == 'Raw Response':  
        #         continue
            
        #     # Check if the key exists in pack_info
        #     if key not in pack_info['Alarms']:
        #         errors.append(f"\nAlarms {key} missing in pack_info.")
        #         continue

        #     actual_value = pack_info['Alarms'][key]

        #     # Handle multiple possible valid responses
        #     if isinstance(expected_value, list):
        #         if actual_value not in expected_value:
        #             errors.append(
        #                 f"\nAlarms {key} mismatch:\n"
        #                 f"Expected one of -> {expected_value}\n"
        #                 f"Received -> {actual_value}"
        #             )
        #     # Handle single expected value
        #     elif actual_value != expected_value:
        #         errors.append(
        #             f"\nAlarms {key} mismatch:\n"
        #             f"Expected -> {expected_value}\n"
        #             f"Received -> {actual_value}"
        #         )

        # Validate Function Switch Parameters
        for key, expected_value in criteria['Function Switch Param'].items():
            if key not in pack_info.get('Function Switch Param', {}):
                errors.append(f"\nFunction Switch Parameter - {key} missing in pack_info.")
                continue

            actual_value = pack_info['Function Switch Param'][key]
            if isinstance(expected_value, list):
                if actual_value not in expected_value:
                    errors.append(
                        f"\nFunction Switch - {key} mismatch:\n"
                        f"Expected one of -> {expected_value}\n"
                        f"Received -> {actual_value}"
                    )
            elif actual_value != expected_value:
                errors.append(
                    f"\nFunction Switch - {key} mismatch:\n"
                    f"Expected -> {expected_value}\n"
                    f"Received -> {actual_value}"
                )

        # Validate Basic Parameters
        for key, value in criteria['Basic Param'].items():
            if key in 'Raw Response':
                continue  # Skip these fields
            if isinstance(value, list):  # Range check
                if not (value[0] <= pack_info['Basic Param'][key] <= value[1]):
                    errors.append(f"\nBasic Param - {key} out of range: {pack_info['Basic Param'][key]} not in {value}")
            else:  # Exact match
                if pack_info['Basic Param'][key] != value:
                    errors.append(f"\nBasic Param - {key} mismatch:\nExpected -> {value}\nReceived -> {pack_info['Basic Param'][key]}")


        for key, value in criteria['Acquire Device Manufacture Info'].items():
            if key == ['Manufacturer', 'Device Name','BMS Serial Number','Pack Serial Number']:  # Skip this field in PIC
                continue
            if pack_info['Acquire Device Manufacture Info'][key] != value:
                #errors.append(f"Acquire Device Manufacture Info {key} mismatch:\nExpected firmware version -> {value[0]}.{value[1]}\nReceived firmware version -> {pack_info['Acquire Device Manufacture Info'][key][0]}.{pack_info['Acquire Device Manufacture Info'][key][1]}")
                errors.append(f"\nExpected firmware version -> {value}\nReceived firmware version -> {pack_info['Acquire Device Manufacture Info'][key]}")

        return errors

    def run_test(self,serial_number):
        bms = BMSCommunicator(port='/dev/ttyUSB0', baudrate=19200)
        pack_info = bms.get_pack_info()
        pack_time = datetime.datetime.now()
        formatted_pack_time = pack_time.strftime('%Y-%m-%d %H:%M:%S%f')[:-6]
        
        # Add Test_Info section with operator and timestamp
        pack_info["Test_Info"] = {
            "Operator": self.current_operator,
            "Timestamp": formatted_pack_time
        }
        
        # Save to both files
        pack_filename = f"{serial_number}_complete_pack_info.json"
        print(f'Pack file name: {pack_filename}')


        if self.NBP_checkbox.get():
            #Store On Pi
            pack_filepath = os.getcwd() + "/Complete_Pack_Info_dump/Production/" + pack_filename
            pack_ftp_folder = 'BMS_Test_Station_New/complete_pack_data/Production'

            json_path = os.path.join("Complete_Pack_Info_dump/Production/", pack_filename)
            with open(json_path, 'w') as f:
                json.dump(pack_info, f, indent=4)
            
            # Also update BMS_username.json if needed
            username_path = os.path.join("Complete_Pack_Info_dump/Production/", pack_filename)
            if os.path.exists(username_path):
                with open(username_path, 'w') as f:
                    json.dump(pack_info, f, indent=4)

            #Store on ftp server
            store_pack_info(pack_ftp_folder,pack_filepath,pack_filename) # OUTPUT

        if self.RMA_checkbox.get():
            #Store On Pi
            pack_filepath = os.getcwd() + "/Complete_Pack_Info_dump/RMA/" + pack_filename
            pack_ftp_folder = 'BMS_Test_Station_New/complete_pack_data/RMA'

            json_path = os.path.join("Complete_Pack_Info_dump/RMA/", pack_filename)
            with open(json_path, 'w') as f:
                json.dump(pack_info, f, indent=4)
            
            # Also update BMS_username.json if needed
            username_path = os.path.join("Complete_Pack_Info_dump/RMA/", pack_filename)
            if os.path.exists(username_path):
                with open(username_path, 'w') as f:
                    json.dump(pack_info, f, indent=4)

            #Store on ftp server
            store_pack_info(pack_ftp_folder,pack_filepath,pack_filename) # OUTPUT

        bms.close()

        return pack_info
    
    def load_json(self, serial_number):
        try:
            with open(f'{serial_number}.json', 'r') as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            messagebox.showerror("Error", "JSON file not found. Please run the test first.")
            return None

    def reset_gui(self):

        
        self.serial_entry.delete(0, "end")
        self.serial_entry2.configure(state="normal")
        self.serial_entry2.delete(0,"end")
        self.serial_entry3.configure(state="normal")
        self.serial_entry3.delete(0,"end")

        self.result_text.delete("1.0", "end")
        self.start_button.configure(state="normal")
        self.reset_button.configure(state="disabled")      
        self.status_indicator.configure(text="Ready", text_color="yellow")
        self.inspection_checkbox.deselect() #Liam
        self.NBP_checkbox.deselect()
        self.RMA_checkbox.deselect()
        self.serial_entry2.configure(state="normal")
        self.serial_entry3.configure(state="normal")

    def display_results(self, pack_info):
        self.result_text.delete("1.0", "end")
        
        # Add some styling to the output
        self.result_text.insert("end", "📊 Test Results\n", "heading")
        self.result_text.insert("end", "=" * 50 + "\n\n")
        
        # Device Info
        self.result_text.insert("end", "📱 Device Information\n", "subheading")
        info = pack_info['Acquire Device Manufacture Info']
        for key, value in info.items():
            self.result_text.insert("end", f"{key}: {value}\n")
        
        # PIA Info
        self.result_text.insert("end", "\n🔋 Battery Status (PIA)\n", "subheading")
        pia = pack_info['PIA']
        for key, value in pia.items():
            if key != 'Raw Response':
                self.result_text.insert("end", f"{key}: {value}\n")
                
        # PIB Info
        pib = pack_info['PIB']
        self.result_text.insert("end", "\n🔋 Battery Status (PIB)\n", "subheading")
        for i in range(1, 17):
            self.result_text.insert("end", f"Cell {i} Voltage: {pib.get(f'Cell {i} Voltage', 'N/A')} V\n")
        for i in range(1, 3):
            self.result_text.insert("end", f"Cell Temperature {i}: {pib.get(f'Cell Temperature {i}', 'N/A')} °C\n")
        self.result_text.insert("end", f"Environment Temperature: {pib.get('Environment Temperature', 'N/A')} °C\n")
        self.result_text.insert("end", f"Power Temperature: {pib.get('Power Temperature', 'N/A')} °C\n")
        #self.result_text.insert("end", f"Raw Response: {pib.get('Raw Response', 'N/A')}\n")
        
        # PIC Info
        pic = pack_info['PIC']
        self.result_text.insert("end", "\n🔋 Battery Status (PIC)\n", "subheading")
        self.result_text.insert("end", f"System State Code: {pic.get('System State Code', 'N/A')}\n")
        self.result_text.insert("end", f"FET Event Code: {pic.get('FET Event Code', 'N/A')}\n")
        self.result_text.insert("end", f"Hard Fault Event Code: {pic.get('Hard Fault Event Code', 'N/A')}\n")
        #self.result_text.insert("end", f"Raw Response: {pic.get('Raw Response', 'N/A')}\n")

        # # Alarms Info
        # self.result_text.insert("end", "\n🔋 Battery Status (Alarms)\n", "subheading")
        # alarms = pack_info['Alarms']
        # for key, value in alarms.items():
        #     if key != 'Raw Response':
        #         self.result_text.insert("end", f"{key}: {value}\n")

        # Funtion Switch Parameters
        self.result_text.insert("end", "\n🔋 Battery Status (Function Switch Parameters)\n", "subheading")
        function_switch = pack_info['Function Switch Param']
        for key, value in function_switch.items():
            if key != 'Raw Response':
                self.result_text.insert("end", f"{key}: {value}\n")
        
        # # Basic Parameters
        self.result_text.insert("end", "\n🔋 Battery Status (Basic Parameters)\n", "subheading")
        function_switch = pack_info['Basic Param']
        for key, value in function_switch.items():
            if key != 'Raw Response':
                self.result_text.insert("end", f"{key}: {value}\n")     


    def toggle_login(self):
        if self.current_operator:
            self.logout()
        else:
            self.show_login_dialog()

    def show_login_dialog(self):

        login_window = ctk.CTkToplevel()
        login_window.title("Operator Login")
        login_window.geometry("300x350")  # Increased height to accommodate password
        login_window.resizable(False, False)
        
        # Center the window
        x = self.winfo_x() + (self.winfo_width() // 2) - (300 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (350 // 2)
        login_window.geometry(f"400x450+{x}+{y}")
        
        # Main frame
        main_frame = ctk.CTkFrame(login_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame, 
            text="Operator Login", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Username
        name_label = ctk.CTkLabel(
            main_frame, 
            text="Username:",
            font=ctk.CTkFont(size=14)
        )
        name_label.pack(pady=(10, 5))
        
        name_entry = ctk.CTkEntry(
            main_frame,
            width=200,
            placeholder_text="Enter username"
        )
        name_entry.pack(pady=10)
        
        # Password
        password_label = ctk.CTkLabel(
            main_frame, 
            text="Password:",
            font=ctk.CTkFont(size=14)
        )
        password_label.pack(pady=(10, 5))
        
        password_entry = ctk.CTkEntry(
            main_frame,
            width=200,
            placeholder_text="Enter password",
            show="*"  # Mask password input
        )
        password_entry.pack(pady=10)

                    
        def validate_login():

            # Checks User login, removes spaces and converts all to UpperCase
            time.sleep(0.1)
            entered_operator = ''.join(name_entry.get().split()).upper()
            time.sleep(0.1)
            entered_password = password_entry.get().strip()

            if  entered_operator in self.configLogin['Users'] and self.configLogin['Users'][entered_operator] == entered_password:

                self.current_operator = entered_operator
                self.operator_label.configure(text=self.current_operator)
                self.lock_button.configure(fg_color="green")  # Change to green when logged in
                self.start_button.configure(state="normal")
                self.inspection_checkbox.configure(state="normal")  # Enable the checkbox after login
                self.NBP_checkbox.configure(state="normal")
                self.RMA_checkbox.configure(state="normal")
                self.reset_button.configure(state="disabled")
                self.status_indicator.configure(text="Ready", text_color="yellow")
                login_window.destroy()

            else:
                CTkMessagebox(
                    title="Log in Error", 
                    message="Log In Error, please try again",
                    icon="warning"
                )                
                name_entry.delete(0, 'end')
                password_entry.delete(0, 'end')
   
     
        # Sign In button (primary action)
        sign_in_button = ctk.CTkButton(
            main_frame,
            text="Sign In",
            command=validate_login,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        sign_in_button.pack(pady=(30, 10))
        
        # Cancel button (secondary action)
        cancel_button = ctk.CTkButton(
            main_frame,
            text="Cancel",
            command=login_window.destroy,
            width=200,
            height=40,
            fg_color="transparent",
            border_width=2,
            font=ctk.CTkFont(size=14)
        )
        cancel_button.pack(pady=(0, 10))
        
        # Handle window closing
        def on_closing():
            login_window.destroy()

            
        login_window.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Make window modal
        login_window.transient(self)

        # Focus on name entry
        name_entry.focus_set()
        
        # Bind Enter key to validate_login
        name_entry.bind("<Return>", lambda event: validate_login())

    def logout(self):
        self.tester = None 
        self.current_operator = None
        self.jobnr = 0
        self.serial_entry.delete(0, "end")
        self.serial_entry2.delete(0,"end")       
        self.operator_label.configure(text="Not logged in")
        self.lock_button.configure(fg_color="red")  # Change to red when logged out
        self.start_button.configure(state="disabled")  # Disable start button
        self.reset_button.configure(state="disabled")  # Disable reset button
        self.status_indicator.configure(text="Not logged in", text_color="yellow")
        self.inspection_checkbox.deselect()
        self.inspection_checkbox.configure(state="disabled")
        self.NBP_checkbox.deselect()
        self.NBP_checkbox.configure(state="disabled")
        self.RMA_checkbox.deselect()
        self.RMA_checkbox.configure(state="disabled")
        #self.login_window.destroy()

    def validate_credentials(self, username, pin):
        users = self.configLogin.get('Users', {})
        return username in users and users[username] == pin

if __name__ == "__main__":
    app = BMSTestApp()
    app.mainloop()
