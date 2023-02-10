from asyncio.windows_events import NULL
import json
import math
import tkinter as tk
from tkinter import Toplevel
import datetime as dt

# Import JSON files Globally
profile = json.load(open("json_files/profile.json"))
status = json.load(open("json_files/status.json"))
quests = json.load(open("json_files/quests.json"))
# Make index for all stats
stat_list = dict()
i = 0
for stat in status:
    stat_list[stat["acronym"]] = i
    i += 1

def set_exp_target(level):
    exp_goal = int(1000/(1+math.exp(-0.1*(level-30)))-42)
    return exp_goal
# Initialize Next Level Requirements
for stat in status:
    stat["next_level"] = set_exp_target(stat["value"])
    stat["prev_level"] = set_exp_target(stat["value"]-1)
    with open("json_files/status.json", "w") as stat_file:
        json.dump(status, stat_file)

# Keep Track of Quests that are Showing
showing = []

#  Main Functions
def refresh_status(stats_frame):
    global status
    status = json.load(open("json_files/status.json"))
    stat_keys = list(stat_list.keys())
    for row in range(len(status)):
        stat_name = tk.Label(stats_frame, text=stat_keys[row]+":", font="Arial 15")
        stat_name.grid(column=0, row=row)
        stat_val = tk.Label(stats_frame, text=status[stat_list[stat_keys[row]]]["value"], font="Arial 15")
        stat_val.grid(column=1, row=row)
        percent = status[stat_list[stat_keys[row]]]["current_exp"]/status[stat_list[stat_keys[row]]]["next_level"]*100
        percent = str(format(percent, '.1f'))+'%'
        stat_progress = tk.Label(stats_frame, text='... '+percent, font="Arial 15")
        stat_progress.grid(column=2, row=row)
    
def change_status(stat, change):
    stat_index = stat_list[stat]
    stat = status[stat_index]
    stat["current_exp"] = stat["current_exp"] + change
    if (stat["current_exp"] >= stat["next_level"]):   #level up condition
        stat["value"] += 1  #increase stat value
        difference = stat["current_exp"] - stat["next_level"]   #update exp
        stat["current_exp"] = difference
        stat["next_level"] = set_exp_target(stat["value"])  #set new exp target
    elif (stat["current_exp"] < 0):     #drop level condition
        while (stat["current_exp"] < 0):
            stat["value"] -= 1
            difference = stat["prev_level"] + stat["current_exp"]
            stat["current_exp"] = difference
            stat["next_level"] = set_exp_target(stat["value"])
            stat["prev_level"] = set_exp_target(stat["value"]-1)
            if (stat["value"] < 0):
                stat["current_exp"] = 0
                stat["value"] = 0
                break
    with open("json_files/status.json", "w") as stat_file:
        json.dump(status, stat_file)
    return 1

def set_showing_false(quest_id_array):
    for quest_id in quest_id_array:
        quests[quest_id]["showing"] = False
    with open("json_files/quests.json", "w") as quest_file:
        json.dump(quests, quest_file)
    return 1

class quest_window(Toplevel):
    global showing
    #  Constructor
    def __init__(self, quest_number, quest_status, status_frame, master = None):
        super().__init__(master = master)
        # Tkinter Setup
        self.title("Quest")
        self.protocol("WM_DELETE_WINDOW", self.exit)
        
        # Initial Variables
        self.quest_number = quest_number
        self.status_frame = status_frame
        self.quest_status = quest_status
        
        title = tk.Label(self, text=quests[quest_number]["title"], font="Arial 17")
        title.pack(side="top")
        description = tk.Label(self, text=quests[quest_number]["description"], font="Arial 12", wraplength=300)
        description.pack(side="top")
        
        if (quest_status == "ongoing" or quest_status == "repeat"):    
            # Rewards
            rewards_frame = tk.Frame(self)
            rewards_frame.pack(side="top")
            reward_stats = list(quests[quest_number]["reward"][0].keys())
            reward_vals = list(quests[quest_number]["reward"][0].values())
            reward_title = tk.Label(rewards_frame, text="Rewards:", font="Arial 17")
            reward_title.grid(row=0, column=1)
            for i in range (len(reward_stats)):
                stat = tk.Label(rewards_frame, text=reward_stats[i])
                stat.grid(column=0, row=i+1)
                upgrade = tk.Label(rewards_frame, text='+' + str(reward_vals[i]))
                upgrade.grid(column=2, row=i+1)
            # Penalty
            penalty_frame = tk.Frame(self)
            penalty_frame.pack(side="top")
            penalty_stats = list(quests[quest_number]["penalty"][0].keys())
            penalty_vals = list(quests[quest_number]["penalty"][0].values())
            penalty_title = tk.Label(penalty_frame, text="Penalties:", font="Arial 17")
            penalty_title.grid(row=0, column=1)
            for i in range (len(penalty_stats)):
                stat = tk.Label(penalty_frame, text=penalty_stats[i])
                stat.grid(column=0, row=i+1)
                downgrade = tk.Label(penalty_frame, text=str(penalty_vals[i]))
                downgrade.grid(column=2, row=i+1)
            # Buttons
            button_frame = tk.Frame(self)
            button_frame.pack(side="bottom")
            complete_button = tk.Button(button_frame, command=lambda:finish_quest(quest_number,"completed", status_frame, self), text="Complete Quest!", font="Arial 17")
            complete_button.grid(column=0, row=0)
            fail_button = tk.Button(button_frame, command=lambda:finish_quest(quest_number,"failed", status_frame, self), text="Fail Quest T.T", font="Arial 17")
            fail_button.grid(column=2, row=0)
            if (quests[quest_number]['repeat'] == 1):
                pass_button = tk.Button(button_frame, command=lambda:finish_quest(quest_number,"passed", status_frame, self), text="Skip Quest...", font="Arial 17")
                pass_button.grid(column=1, row=0)
            edit_button = tk.Button(button_frame, command=lambda:quest_editor_window(master, self.quest_number), text="Edit Quest", font="Arial 17")
            edit_button.grid(column=1, row=1)
        #  Duration
            now = dt.datetime.now().strftime("%m/%d/%H:%M")
            now = dt.datetime.strptime(now,"%m/%d/%H:%M")
            due = dt.datetime.strptime(quests[quest_number]["complete_by"],"%m/%d/%H:%M")

            time_left = str(due-now)
            self.duration = tk.Label(self, text="Time Left: \n"+time_left, font="Arial 17")
            self.duration.pack(side="top")
            if (quests[quest_number]["repeat"] == 1):
                tk.Label(self, text="Repeat Quest", font="Arial 17").pack(side="top")

    def exit(self):
        for quest_window in showing:
            if (quest_window[1] == self.quest_number):
                showing.remove(quest_window)
        quests[self.quest_number]["showing"] = False
        with open("json_files/quests.json", "w") as quest_file:
            json.dump(quests, quest_file)
        self.destroy()
        return 1
        
    def update(self):
        now = dt.datetime.now().strftime("%m/%d/%H:%M")
        now = dt.datetime.strptime(now,"%m/%d/%H:%M")
        due = dt.datetime.strptime(quests[self.quest_number]["complete_by"],"%m/%d/%H:%M")
        time_left = str(due-now)
        
        self.duration.destroy()
        self.duration = tk.Label(self, text="Time Left: \n"+time_left, font="Arial 17")
        self.duration.pack(side="top")
        return 1
            
def finish_quest (quest_number, finish_status, status_frame, quest_root):
    global showing
    for quest_window in showing:
        if (quest_window[1] == quest_number):
            showing.remove(quest_window)
    
    # Change JSON
    if (finish_status == "completed"):
        result = "reward"
        quests[quest_number][finish_status] = not quests[quest_number][finish_status]
        # Apply Stats Changes
        stats = list(quests[quest_number][result][0])
        for stat in stats:
            val = quests[quest_number][result][0][stat]
            change_status(stat, val)
    elif (finish_status == "failed"):
        result = "penalty"
        quests[quest_number][finish_status] = not quests[quest_number][finish_status]
        # Apply Stats Changes
        stats = list(quests[quest_number][result][0])
        for stat in stats:
            val = quests[quest_number][result][0][stat]
            change_status(stat, val)
    elif (finish_status == "passed"):
        quests[quest_number]["completed"] = not quests[quest_number]["completed"]
    
    with open("json_files/quests.json", "w") as quest_file:
        json.dump(quests, quest_file)
    refresh_status(status_frame) 
    
    if (quest_root != NULL):
        quest_root.destroy()           
    
    return 1

def show_quest(type, status_frame):
    global showing
    ongoing_quests = []
    completed_quests = []
    failed_quests = []
    repeat_quests = []
    i = 0
    for quest in quests:
        if (quest["completed"] == False and quest["failed"] == False and quest["repeat"] == 0):
            ongoing_quests.append(i)
        elif (quest["completed"] == False and quest["failed"] == False and quest["repeat"] == 1):
            repeat_quests.append(i)
        elif (quest["completed"] == True and quest["failed"] == False and quest["repeat"] == 0):
            completed_quests.append(i)
        elif (quest["failed"] == True and quest["completed"] == False and quest["repeat"] == 0):
            failed_quests.append(i)
        i += 1
        
    quest_list = []
    if (type == "ongoing"):
        quest_list = ongoing_quests
    elif (type == "completed"):
        quest_list = completed_quests
    elif (type == "failed"):
        quest_list = failed_quests
    elif(type == "repeat"):
        quest_list = repeat_quests
        
    for quest_number in quest_list:
        if (quests[quest_number]["showing"] == False):
            quest = quest_window(quest_number, type, status_frame)
            showing.append([quest, quest_number])
            quests[quest_number]["showing"] = True
        with open("json_files/quests.json", "w") as quest_file:
            json.dump(quests, quest_file)
    return 1

def make_quest(quest_maker,quest_number, title, description, rewards_array, penalties_array, duration, repeat):
    rewards_list = [reward.get() for reward in rewards_array]
    penalties_list = [penalty.get() for penalty in penalties_array]
    
    new_quest = {
        "quest_number": quest_number,
        "title": title,
        "description": description,
        "reward": [],
        "penalty": [],
        "duration": int(duration),
        "completed": False,
        "failed": False,
        "created_date": dt.datetime.now().strftime("%m/%d/%H:%M"),
        "complete_by": (dt.datetime.now() + dt.timedelta(days=int(duration))).strftime("%m/%d/%H:%M"),
        "repeat": repeat,
        "showing": False
    }
    
    rewards_dict = {}
    penalties_dict = {}
    stats = list(stat_list.keys())
    for i in range (len(stat_list)):
        if (rewards_list[i] != ''):
            rewards_dict[stats[i]] = float(rewards_list[i])
    for i in range (len(stat_list)):
        if (penalties_list[i] != ''):
            penalties_dict[stats[i]] = float(penalties_list[i])

    new_quest["reward"].append(rewards_dict)
    new_quest["penalty"].append(penalties_dict)
    
    quests.append(new_quest)
    with open("json_files/quests.json", "w") as quest_file:
        json.dump(quests, quest_file)
    
    quest_maker.destroy()
    return 1

def edit_quest(quest_editor,quest_number, title, description, rewards_array, penalties_array, duration, repeat):
    rewards_list = [reward.get() for reward in rewards_array]
    penalties_list = [penalty.get() for penalty in penalties_array]
    
    quests[quest_number]['title'] = title
    quests[quest_number]['description'] = description
    quests[quest_number]['repeat'] = repeat
    quests[quest_number]['duration'] = int(duration)
 
    rewards_dict = {}
    penalties_dict = {}
    stats = list(stat_list.keys())
    for i in range (len(stat_list)):
        if (rewards_list[i] != ''):
            rewards_dict[stats[i]] = float(rewards_list[i])
    for i in range (len(stat_list)):
        if (penalties_list[i] != ''):
            penalties_dict[stats[i]] = float(penalties_list[i])

    quests[quest_number]["reward"][0] = rewards_dict
    quests[quest_number]["penalty"][0] = penalties_dict
    
    with open("json_files/quests.json", "w") as quest_file:
        json.dump(quests, quest_file)
    
    quest_editor.destroy()
    return 1

def quest_maker_window(tk_root):
    quest_maker = Toplevel(tk_root)
    
    quest_number = len(quests)
    
    title = tk.Label(quest_maker, text="Title:", font="Arial 17")
    title.pack(side="top")
    title_entry = tk.Entry(quest_maker, width=50)
    title_entry.pack(side="top")
    description = tk.Label(quest_maker, text="Description:", font="Arial 17")
    description.pack(side="top")
    description_entry = tk.Text(quest_maker, width=50, height=3, wrap="word")
    description_entry.pack(side="top")
    
    rewards_frame = tk.Frame(quest_maker)
    rewards_frame.pack(side="top")
    rewards_label = tk.Label(rewards_frame, text="REWARDS", font="Arial 17")
    rewards_label.grid(column=0, row=0)
    penalty_frame = tk.Frame(quest_maker)
    penalty_frame.pack(side="top")
    penalty_label = tk.Label(penalty_frame, text="PENALTIES", font="Arial 17")
    penalty_label.grid(column=0, row=0)
    row = 1
    rewards_entry_list = []
    penalties_entry_list = []
    for stat in status:
        tk.Label(rewards_frame, text=str(stat["name"])).grid(column=0, row=row)
        reward = tk.Entry(rewards_frame)
        reward.grid(column=1, row=row)
        rewards_entry_list.append(reward)
        tk.Label(penalty_frame, text=str(stat["name"])).grid(column=0, row=row)
        penalty = tk.Entry(penalty_frame)
        penalty.grid(column=1, row=row)
        penalties_entry_list.append(penalty)
        row +=1
    
    tk.Label(quest_maker, text="Duration in Days:").pack(side="top")
    duration_entry = tk.Entry(quest_maker)
    duration_entry.pack(side="top")
    
    repeat = tk.IntVar()
    tk.Checkbutton(quest_maker, text="Repeat Quest?",onvalue = 1, offvalue = 0,variable = repeat).pack(side="top")
    
    submit_button = tk.Button(quest_maker, text="Make Quest", command=lambda:make_quest(quest_maker,quest_number, title_entry.get(), description_entry.get("1.0",'end-1c'), rewards_entry_list, penalties_entry_list, duration_entry.get(),repeat.get()))
    submit_button.pack(side="top")
    return 1

def quest_editor_window(tk_root, quest_number):
    quest_maker = Toplevel(tk_root)
    
    title = tk.Label(quest_maker, text="Title:", font="Arial 17")
    title.pack(side="top")
    title_entry = tk.Entry(quest_maker, width=50)
    title_entry.insert(0,quests[quest_number]['title'])
    title_entry.pack(side="top")
    description = tk.Label(quest_maker, text="Description:", font="Arial 17")
    description.pack(side="top")
    description_entry = tk.Text(quest_maker, width=50, height=3, wrap="word")
    description_entry.insert(tk.END,quests[quest_number]['description'])
    description_entry.pack(side="top")
    
    rewards_frame = tk.Frame(quest_maker)
    rewards_frame.pack(side="top")
    rewards_label = tk.Label(rewards_frame, text="REWARDS", font="Arial 17")
    rewards_label.grid(column=0, row=0)
    penalty_frame = tk.Frame(quest_maker)
    penalty_frame.pack(side="top")
    penalty_label = tk.Label(penalty_frame, text="PENALTIES", font="Arial 17")
    penalty_label.grid(column=0, row=0)
    row = 1
    rewards_entry_list = []
    penalties_entry_list = []
    for stat in status:
        tk.Label(rewards_frame, text=str(stat["name"])).grid(column=0, row=row)
        reward = tk.Entry(rewards_frame)
        if (stat["acronym"] in quests[quest_number]['reward'][0].keys()):
            reward.insert(0,quests[quest_number]['reward'][0][stat["acronym"]])
        reward.grid(column=1, row=row)
        rewards_entry_list.append(reward)
        tk.Label(penalty_frame, text=str(stat["name"])).grid(column=0, row=row)
        penalty = tk.Entry(penalty_frame)
        if (stat["acronym"] in quests[quest_number]['penalty'][0].keys()):
            penalty.insert(0,quests[quest_number]['penalty'][0][stat["acronym"]])
        penalty.grid(column=1, row=row)
        penalties_entry_list.append(penalty)
        row +=1
    
    tk.Label(quest_maker, text="Duration in Days:").pack(side="top")
    duration_entry = tk.Entry(quest_maker)
    duration_entry.insert(0, quests[quest_number]['duration'])
    duration_entry.pack(side="top")
    
    repeat = tk.IntVar()
    repeat_button = tk.Checkbutton(quest_maker, text="Repeat Quest?",onvalue = 1, offvalue = 0,variable = repeat)
    if (quests[quest_number]['repeat'] == 1):
        repeat_button.select()
    repeat_button.pack(side="top")
    
    submit_button = tk.Button(quest_maker, text="Edit Quest", command=lambda:edit_quest(quest_maker,quest_number, title_entry.get(), description_entry.get("1.0",'end-1c'), rewards_entry_list, penalties_entry_list, duration_entry.get(),repeat.get()))
    submit_button.pack(side="top")
    return 1

def check_overdue(root, status_frame, quest_root):
    now = dt.datetime.strptime(dt.datetime.now().strftime("%m/%d/%H:%M"),"%m/%d/%H:%M")
    for quest_window in showing:
        quest_window[0].update()
    for quest in quests:
        if (dt.datetime.strptime(quest["complete_by"], "%m/%d/%H:%M") < now):
        # if ongoing quest (not)
            if (quest["completed"] == False and quest["failed"] == False):
                # Fail ongoing quest if overdue
                finish_quest(quest["quest_number"], "failed", status_frame, quest_root)
            # if it is a repeat quest, reset quest data
            if (quest["repeat"] == 1): # If daily quest has been completed
                    # reset for next repeat
                    quest["completed"] = False 
                    quest["failed"] = False 
                    quest["complete_by"] = ( dt.datetime.strptime(quest["complete_by"], "%m/%d/%H:%M") + dt.timedelta(days=int(quest["duration"])) ).strftime("%m/%d/%H:%M")
                    with open("json_files/quests.json", "w") as quest_file:
                        json.dump(quests, quest_file)
        
    root.after(60000, check_overdue, root, status_frame, NULL)
    
def runTK ():
    root = tk.Tk()
    root.title('Status Board')
    root.iconbitmap("favicon.ico")
    
    root.attributes('-topmost', True)
    root.update()
    
    # Title
    title_frame = tk.Frame(root)
    title_frame.pack(side="top")
    program_title = tk.Label(title_frame, text="Status Board", font="Arial 20",)
    program_title.pack()
    
    # Profile
    profile_frame = tk.Frame(root)
    profile_frame.pack(side="top")
    profile_keys = list(profile.keys())
    profile_vals = list(profile.values())
    for row in range(len(profile)-1):
        profile_key = tk.Label(profile_frame, text=profile_keys[row]+":", font="Arial 17")
        profile_key.grid(column = 0, row=row)
        profile_val = tk.Label(profile_frame, text=profile_vals[row], font="Arial 17")
        profile_val.grid(column = 1, row=row)
        
    # Stats
    stats_frame = tk.Frame(root)
    stats_frame.pack(side="top")
    stat_keys = list(stat_list.keys())
    for row in range(len(status)):
        stat_name = tk.Label(stats_frame, text=stat_keys[row]+":", font="Arial 15")
        stat_name.grid(column=0, row=row)
        stat_val = tk.Label(stats_frame, text=status[stat_list[stat_keys[row]]]["value"], font="Arial 15")
        stat_val.grid(column=1, row=row)
        percent = status[stat_list[stat_keys[row]]]["current_exp"]/status[stat_list[stat_keys[row]]]["next_level"]*100
        percent = str(format(percent, '.1f'))+'%'
        stat_progress = tk.Label(stats_frame, text='... '+percent, font="Arial 15")
        stat_progress.grid(column=2, row=row)
    
    # Quests
    quests_frame = tk.Frame(root)
    quests_frame.pack(side="bottom")
    show_ongoing_quest = tk.Button(quests_frame, command=lambda:show_quest("ongoing", stats_frame), text="Main Quests", font="Arial 17")
    show_ongoing_quest.grid(column=1, row=1)
    show_repeat_quest =  tk.Button(quests_frame, command=lambda:show_quest("repeat", stats_frame), text="Repeat Quests", font="Arial 17")
    show_repeat_quest.grid(column=2, row=1)
    show_make_quest = tk.Button(quests_frame, command=lambda:quest_maker_window(root), text="Make Quest", font="Arial 17")
    show_make_quest.grid(column=3, row=1)
    show_completed_quest = tk.Button(quests_frame, command=lambda:show_quest("completed", stats_frame), text="Completed Quests", font="Arial 17")
    show_completed_quest.grid(column=1, row=2)
    show_failed_quest = tk.Button(quests_frame, command=lambda:show_quest("failed", stats_frame), text="Failed Quests", font="Arial 17")
    show_failed_quest.grid(column=2, row=2)
    
    # Check Overdue
    root.after(10, check_overdue, root, stats_frame, NULL)
    
    root.mainloop()
    return 1
    
def main():
    # Run GUI
    runTK()
    # Set all showing to false
    set_showing_false([i for i in range(len(quests))])
    return 1

main()