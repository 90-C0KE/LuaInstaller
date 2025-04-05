# Lua Downloader & Installer
# By 1k0de

import os
import shutil
import winreg
from io import BytesIO
from time import sleep
from zipfile import ZipFile
from rich.console import Console
from rich.progress import Progress
from urllib.request import urlopen

console = Console()
console._log_render.omit_repeated_times = False

workingLua_url = "https://github.com/90-C0KE/WorkingLua/archive/main.zip"

def has_admin():
    if os.name == "nt":
        try:
            temp = os.listdir(os.sep.join([os.environ.get("SystemRoot", "C:\\Windows\\"), "temp"]))
        except:
            return (os.environ['USERNAME'], False)
        else:
            return (os.environ['USERNAME'], True)

def modify_user_path_variable(add_path=None, remove_path=None):
    """
    Modify the user-specific PATH environment variable.
    
    Parameters:
        add_path (str): The path to add to the PATH variable. (Default: None)
        remove_path (str): The path to remove from the PATH variable. (Default: None)
        
    Returns:
        str: A message indicating success or failure.
    """
    # Define the registry key and value
    key = winreg.HKEY_CURRENT_USER
    subkey = r"Environment"
    value_name = "PATH"
    
    try:
        # Open the registry key for reading and writing
        with winreg.OpenKey(key, subkey, 0, winreg.KEY_READ | winreg.KEY_WRITE) as reg_key:
            # Get the current value of the PATH variable
            current_value, reg_type = winreg.QueryValueEx(reg_key, value_name)
            
            # Modify the PATH value if necessary
            if add_path:
                # Add the new path if it's not already in the PATH
                if add_path not in current_value:
                    current_value += f";{add_path}"
                    print(f"Adding {add_path} to PATH.")
                else:
                    print(f"{add_path} is already in PATH.")
            
            if remove_path:
                # Remove the specified path if it exists
                if remove_path in current_value:
                    current_value = current_value.replace(remove_path, "").strip(";")
                    print(f"Removing {remove_path} from PATH.")
                else:
                    print(f"{remove_path} not found in PATH.")
            
            # Update the PATH variable in the registry
            winreg.SetValueEx(reg_key, value_name, 0, reg_type, current_value)
            
        return "User-specific PATH variable updated successfully."
    
    except FileNotFoundError:
        return f"The registry key {subkey} does not exist."
    except PermissionError:
        return "PermissionError: Unable to modify the registry."
    except Exception as e:
        return f"An error occurred: {e}"

def modify_system_path_variable(add_path=None, remove_path=None):
    """
    Modify the system-wide PATH environment variable for the current user.
    
    Parameters:
        add_path (str): The path to add to the PATH variable. (Default: None)
        remove_path (str): The path to remove from the PATH variable. (Default: None)
        
    Returns:
        str: A message indicating success or failure.
    """
    # Define the registry key and value
    key = winreg.HKEY_LOCAL_MACHINE
    subkey = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
    value_name = "PATH"
    
    try:
        # Open the registry key for reading and writing
        with winreg.OpenKey(key, subkey, 0, winreg.KEY_READ | winreg.KEY_WRITE) as reg_key:
            # Get the current value of the PATH variable
            current_value, reg_type = winreg.QueryValueEx(reg_key, value_name)
            #print(f"Current PATH value: {current_value}")  # Debug: check the current PATH value
            
            # Modify the PATH value if necessary
            if add_path:
                # Add the new path if it's not already in the PATH
                if add_path not in current_value:
                    current_value += f";{add_path}"
                    print(f"Adding {add_path} to system PATH.")
                else:
                    print(f"{add_path} is already in system PATH.")
            
            if remove_path:
                # Remove the specified path if it exists
                if remove_path in current_value:
                    current_value = current_value.replace(remove_path, "").strip(";")
                    print(f"Removing {remove_path} from system PATH.")
                else:
                    print(f"{remove_path} not found in system PATH.")
            
            # Update the PATH variable in the registry
            winreg.SetValueEx(reg_key, value_name, 0, reg_type, current_value)
        
        return "System PATH variable updated successfully."
    
    except FileNotFoundError:
        return f"The registry key {subkey} does not exist."
    except PermissionError:
        return "PermissionError: Unable to modify the registry. You might need admin privileges."
    except Exception as e:
        return f"An error occurred: {e}"

def runDownloader():
    console.clear()
    console.rule("[bold white]~=| LUA DOWNLOADER |=~")

    console.print("\nChecking user privileges...")
    sleep(0.5)

    isAdmin = has_admin() #('username', True/False)
    downloadPath = ""

    if isAdmin[1]:
        console.print("User has admin privileges ✅")
        downloadPath = "C:\\Program Files\\"
    else:
        console.print("User does not have admin privileges ❌")
        downloadPath = "C:\\Users\\" + isAdmin[0] + "\\Documents\\"

    sleep(0.5)
    console.print("")
    
    console.log("Beginning download to: " + downloadPath + "...")

    with Progress() as progress:
        download_task = progress.add_task("[cyan]Downloading...", total=None)
        
        http_response = urlopen(workingLua_url)

        chunks = 8192
        download_data = b''

        while True:
            chunk = http_response.read(chunks)
            if not chunk:
                break
            download_data += chunk
        
        progress.update(download_task, total=1, advance=1, completed=True)

        if os.path.exists(f"{downloadPath}lua"):
            shutil.rmtree(f"{downloadPath}lua")

        if os.path.exists(f"{downloadPath}WorkingLua-main"):
            shutil.rmtree(f"{downloadPath}WorkingLua-main")

        if os.path.exists(f"{downloadPath}WorkingLua-main.zip"):
            os.remove(f"{downloadPath}WorkingLua-main.zip")

        zipfile = ZipFile(BytesIO(download_data))

        extraction_task = progress.add_task("[green]Extracting...", total=len(zipfile.namelist()))
        for file_name in zipfile.namelist():
            zipfile.extract(file_name, path=downloadPath)  # Extract each file
            progress.update(extraction_task, advance=1)

    os.rename(f"{downloadPath}WorkingLua-main", f"{downloadPath}lua")

    console.log("Successfully completed download & extraction...")
    console.print("")

    if isAdmin[1]:
        console.log("Checking environment variables for system...")
    else:
        console.log("Checking environment variables for user...")

    requiresSelfEnvironEdit = False

    if isAdmin[1]:
        res = modify_system_path_variable(remove_path=f"{downloadPath}lua\\bin")
        console.log(res)
        res2 = modify_system_path_variable(add_path=f"{downloadPath}lua\\bin")
        console.log(res2)

        if res2 != "System PATH variable updated successfully.":
            requiresSelfEnvironEdit = True
    else:
        res = modify_user_path_variable(remove_path=f"{downloadPath}lua\\bin")
        console.log(res)
        res2 = modify_user_path_variable(add_path=f"{downloadPath}lua\\bin")
        console.log(res2)
        
        if res2 != "User-specific PATH variable updated successfully.":
            requiresSelfEnvironEdit = True

    sleep(1)

    console.clear()
    console.print("[bold white on blue]\n| LUA Downloader completed successfully |")

    if requiresSelfEnvironEdit:
        console.print("NOTE: Must edit environment variables manually, failed to do it automatically.")
    
    console.print("\n[ PRESS ANY KEY ]")
    os.system("pause > nul")
    exit()





def main_menu():
    console.print("[bold white on blue]\n| LUA Downloader & Installer |\n[reset]         | By 1k0de |\n")
    console.print("Would you like to run the downloader?")
    input1 = console.input(prompt="(y / n) > ")

    input1 = input1.lower()
    if input1 == "yes":
        runDownloader()
    elif input1 == "y":
        runDownloader()
    elif input1 == "no":
        exit()
    elif input1 == "n":
        exit()

if __name__ == "__main__":
    console.set_window_title("Lua Downloader | By 1k0de")
    console.clear()
    main_menu()