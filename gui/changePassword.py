import datetime
import time
import tkinter as tk
from database.db import  reset_password_db, verify_user_credentials
import tkinter as tk
from gui.theme_manager import apply_theme  


def update_password(rt,old_password, new_password,new_password2,userDetails):
    oldPass = old_password.get()
    newPass = new_password.get()
    newPass2 = new_password2.get()
    checkOldPassword = verify_user_credentials(userDetails['email'], oldPass)
    print(checkOldPassword)
    if checkOldPassword:
        if newPass == newPass2:
            r = reset_password_db(userDetails['email'], newPass)
            if r:
                tk.messagebox.showinfo("Password Changed", f"Password Updated for: "
                                                           f"\n {userDetails['name']}\n!!!")
                time.sleep(3)
                rt.destroy()
            else:
                tk.messagebox.showinfo("Error Ocurred ", f"Password Not Updated...\ncontact administrator: ")
                rt.destroy()
        else:
            tk.messagebox.showinfo("Error", "Please enter the same password")
    else:
        tk.messagebox.showinfo("Error", "old password does not match")


def change_password(user_details):
    rt = tk.Tk()
    rt.title(f"Change Password...")
    rt.geometry("280x300")
    #user data

    #old Password
    tk.Label(rt, text=f"Changing Password for :\n{ user_details['name']}\n",font=("Times New Roman", 16 ,"bold")).pack()
    tk.Label(rt, text="Enter your old password").pack()
    oldpass = tk.Entry(rt, width=20,show="*")
    oldpass.pack(pady=5)

    tk.Label(rt, text="Enter your New Password").pack()
    newPass = tk.Entry(rt, width=20,show="*")
    newPass.pack(pady=5)

    #Confirm Password
    tk.Label(rt, text="Confirm your New Password").pack()
    newPass2 = tk.Entry(rt, width=20,show="*")
    newPass2.pack(pady=5)

    submit_button = tk.Button(rt, text="Submit",width=15, command=lambda:
    (update_password(rt,oldpass,newPass,newPass2,user_details)))
    submit_button.pack(side="left")
    cancelButton = tk.Button(rt, text="Cancel", width=15,command=lambda:rt.destroy())
    cancelButton.pack(side="right")
    apply_theme(rt)
    rt.mainloop()



