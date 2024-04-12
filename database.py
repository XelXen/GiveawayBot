# GiveawayBot Database Functions
# Made by @xeltexynos
# Version: 1.0.0

# Imports

import pickle
import varfile
import os
from datetime import datetime
from typing import Union


# Debug Functions

def printlog(message: str, end: str = "") -> bool:
    try:
        if end != "":
            print(message, end=end)
        else:
            print(message)
        
        if not varfile.test_mode:
            current_time = datetime.now().strftime(format="%H:%M:%S")
            current_date = datetime.now().strftime(format="%Y-%m-%d")
            if not os.path.exists(path="logs"):
                os.makedirs(name="logs")
            with open(file=(os.path.join("logs", f"database_{current_date}.log")), mode="a+", encoding="utf-8") as log:
                log.write(f"[{current_time}] {message}\n")

        return True
    
    except Exception as e:
        print(e)
        return False


# Low-Level Functions
    
def save_db(data: dict, filename: str = varfile.database) -> bool:
    try:
        with open(file=filename, mode="wb") as f:
            pickle.dump(obj=data, file=f)

        printlog(message=f"Database saved to {filename}")
    
        return True
    
    except Exception as e:
        print(e)
        return False


def load_db(filename: str = varfile.database) -> Union[dict, bool]:
    try:
        with open(file=filename, mode="rb") as f:
            printlog(message=f"Database loaded from {filename}")
            return pickle.load(file=f)

    except Exception as e:
        print(e)
        return False


def clear_db(filename: str = varfile.database) -> bool:
    try:
        with open(file=filename, mode="wb") as f:
            pickle.dump(obj={"codes": [],
                         "users": set(),
                         "chosen": [],
                         "time": {"total": 0, "left": 0},
                         "post_id": None,
                         "used_codes": set(),
                         "banned": set()}, file=f)

        printlog(message=f"Database cleared")

        return True
    
    except Exception as e:
        print(e)
        return False
    

def snapshot(filename: str = varfile.database) -> Union[dict, bool]:
    try:
        if not os.path.exists(path="snapshots"):
            os.makedirs(name="snapshots")
        
        current_time = datetime.now().strftime(format="%H-%M-%S")
        current_date = datetime.now().strftime(format="%Y-%m-%d")
        snapshot_filename = os.path.join("snapshots", f"snapshot_{current_date}_{current_time}.pickle")
        
        with open(file=filename, mode="rb") as f:
            with open(file=snapshot_filename, mode="wb") as s:
                s.write(f.read())
        
        printlog(message=f"Database snapshot created at {snapshot_filename}")

        return True
    
    except Exception as e:
        print(e)
        return False


def create_db(filename: str = varfile.database) -> Union[dict, bool]:
    try:
        with open(file=filename, mode="wb") as f:
            pickle.dump(obj={"codes": [],
                         "users": set(),
                         "chosen": [],
                         "time": {"total": 0, "left": 0},
                         "post_id": None,
                         "used_codes": set(),
                         "banned": set()}, file=f)

        printlog(message=f"Database created at {filename}")

        return load_db(filename=filename)
    
    except Exception as e:
        print(e)
        return False


# Top-Level Functions
    
def add_user(user: int, data: dict = None, filename: str = varfile.database) -> bool:
    if data == None:
        try:
            data = load_db(filename=filename)
        except Exception as e:
            print(e)
            return False

    if not "users" in data:
        data["users"] = set()
    elif user in data["users"]:
        return False

    try:
        data["users"].add(user)
        save_db(data=data, filename=filename)
        printlog(message=f"User {user} added to database")
        return True

    except Exception as e:
        print(e)
        return False


def remove_user(user: int, data: dict = None, filename: str = varfile.database) -> bool:
    if data == None:
        try:
            data = load_db(filename=filename)
        except Exception as e:
            print(e)
            return False

    if not "users" in data:
        data["users"] = set()
        return False
    elif user not in data["users"]:
        return False

    try:
        data["users"].remove(user)
        save_db(data=data, filename=filename)
        printlog(message=f"User {user} removed from database")
        return True

    except Exception as e:
        print(e)
        return False


def add_codes(codes: list, data: dict = None, filename: str = varfile.database) -> bool:
    if data == None:
        try:
            data = load_db(filename=filename)
        except Exception as e:
            print(e)
            return False

    if not "codes" in data:
        data["codes"] = []

    try:
        data["codes"] = codes
        save_db(data=data, filename=filename)
        printlog(message=f"Codes added to database")
        return True

    except Exception as e:
        print(e)
        return False


def mark_used(code: str, data: dict = None, filename: str = varfile.database) -> bool:
    if data == None:
        try:
            data = load_db(filename=filename)
        except Exception as e:
            print(e)
            return False

    if not "codes" in data:
        data["codes"] = []
        return False
    
    if not "used_codes" in data:
        data["used_codes"] = []
    elif code not in data["codes"] or code in data["used_codes"]:
        return False

    try:
        data["used_codes"].add(code)
        save_db(data=data, filename=filename)
        printlog(message=f"Code {code} marked as used")
        return True

    except Exception as e:
        print(e)
        return False


def ban_user(user: int, data: dict = None, filename: str = varfile.database) -> bool:
    if data == None:
        try:
            data = load_db(filename=filename)
        except Exception as e:
            print(e)
            return False

    if not "banned" in data:
        data["banned"] = set()
    elif user in data["banned"]:
        return False

    try:
        data["banned"].add(user)
        save_db(data=data, filename=filename)
        printlog(message=f"User {user} banned")
        return True

    except Exception as e:
        print(e)
        return False


def unban_user(user: int, data: dict = None, filename: str = varfile.database) -> bool:
    if data == None:
        try:
            data = load_db(filename=filename)
        except Exception as e:
            print(e)
            return False

    if not "banned" in data:
        data["banned"] = set()
        return False
    elif user not in data["banned"]:
        return False

    try:
        data["banned"].remove(user)
        save_db(data=data, filename=filename)
        printlog(message=f"User {user} unbanned")
        return True

    except Exception as e:
        print(e)
        return False


def set_post_id(post_id: int, data: dict = None, filename: str = varfile.database) -> bool:
    if data == None:
        try:
            data = load_db(filename=filename)
        except Exception as e:
            print(e)
            return False

    try:
        data["post_id"] = post_id
        save_db(data=data, filename=filename)
        printlog(message=f"Post ID set to {post_id}")
        return True

    except Exception as e:
        print(e)
        return False


def set_time(total: int, left: int = 0, data: dict = None, filename: str = varfile.database) -> bool:
    if data == None:
        try:
            data = load_db(filename=filename)
        except Exception as e:
            print(e)
            return False

    try:
        data["time"] = {"total": total, "left": left}
        save_db(data=data, filename=filename)
        printlog(message=f"Time set to {total} total, {left} left")
        return True

    except Exception as e:
        print(e)
        return False


def mark_chosen(user: int, data: dict = None, filename: str = varfile.database) -> bool:
    if data == None:
        try:
            data = load_db(filename=filename)
        except Exception as e:
            print(e)
            return False

    if not "chosen" in data:
        data["chosen"] = []
    elif user in data["chosen"] or user not in data["users"]:
        return False

    try:
        data["chosen"].append(user)
        data["users"].remove(user)
        save_db(data=data, filename=filename)
        printlog(message=f"User {user} marked as chosen")
        return True

    except Exception as e:
        print(e)
        return False


def clear_chosen(data: dict = None, filename: str = varfile.database) -> bool:
    if data == None:
        try:
            data = load_db(filename=filename)
        except Exception as e:
            print(e)
            return False

    try:
        data["chosen"] = []
        save_db(data=data, filename=filename)
        printlog(message=f"Chosen users cleared")
        return True

    except Exception as e:
        print(e)
        return False


def clear_used(data: dict = None, filename: str = varfile.database) -> bool:
    if data == None:
        try:
            data = load_db(filename=filename)
        except Exception as e:
            print(e)
            return False

    try:
        data["used_codes"] = []
        save_db(data=data, filename=filename)
        printlog(message=f"Used codes cleared")
        return True

    except Exception as e:
        print(e)
        return False


def clear_banned(data: dict = None, filename: str = varfile.database) -> bool:
    if data == None:
        try:
            data = load_db(filename=filename)
        except Exception as e:
            print(e)
            return False

    try:
        data["banned"] = set()
        save_db(data=data, filename=filename)
        printlog(message=f"Banned users cleared")
        return True

    except Exception as e:
        print(e)
        return False

def clear_users(data: dict = None, filename: str = varfile.database) -> bool:
    if data == None:
        try:
            data = load_db(filename=filename)
        except Exception as e:
            print(e)
            return False
        
    try:
        data["users"] = set()
        save_db(data=data, filename=filename)
        printlog(message=f"Users cleared")
        return True

    except Exception as e:
        print(e)
        return False

def clear_post_id(data: dict = None, filename: str = varfile.database) -> bool:
    if data == None:
        try:
            data = load_db(filename=filename)
        except Exception as e:
            print(e)
            return False
        
    try:
        data["post_id"] = None
        save_db(data=data, filename=filename)
        printlog(message=f"Post ID cleared")
        return True

    except Exception as e:
        print(e)
        return False
