
import json
import os
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.table import Table
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
OUTPUT_DIR = os.path.join(BASE_DIR, "analytics")

os.makedirs(OUTPUT_DIR, exist_ok=True)


EXERCISE_NAMES = {
    "left": "4x6",
    "middle": "4x7x8",
    "right": "Seufzer",
    "custom": "Custom",
    "Dankbarkeits\u00fcbung": "Dankbarkeitsübung"        #Dankbarkeitsübung so geschrieben weil Ü immer Probleme bereitet und es mit Dankbarkeits\u00fcbung gelogged wird
}

#Dauer
DURATION_NAMES = {
    60: "1min",
    180: "3min",
    300: "5min"
}

STRESS_ORDER = [
    "Sehr entspannt",
    "Entspannt",
    "Mittel",
    "Etwas gestresst",
    "Gestresst",
    #"Sehr gestresst"
    "keine Angaben"
]

STRESS_RANK = {
    "Sehr entspannt": 5,
    "Entspannt": 4,
    "Mittel": 3,
    "Etwas gestresst": 2,
    "Gestresst": 1,
    #"Sehr gestresst": 1  # jetzt keine Angaben
    "keine Angaben": 6 
}


def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []


def build_exercise_data(session_data, evaluation_data):
    sessions_by_id = {}
    for entry in session_data:
        session_id = entry.get("session_id")
        if session_id:
            sessions_by_id[session_id] = entry
            



    exercise_data = {}
    for exercise_key in EXERCISE_NAMES.keys():
        exercise_data[exercise_key] = {
            60: {"before": [], "after": []},
            180: {"before": [], "after": []},
            300: {"before": [], "after": []},
        }


    for entry in session_data:
        session_id = entry.get("session_id")
        choice = entry.get("choice")
        duration = entry.get("duration")
        stress_before = entry.get("stress_before")

        if not session_id or not choice or not duration:
            continue

        if choice not in exercise_data:
            # Fallback: unbekannte bung ignorieren, aber loggen
            print(f"? Unbekannte Übung in session_log: '{choice}'")
            continue

        if duration <= 60:
            dur_key = 60
        elif duration <= 180:
            dur_key = 180
        else:
            dur_key = 300

        if stress_before and stress_before != "N/A":
            stress_name = stress_before.replace(".png", "")
            exercise_data[choice][dur_key]["before"].append(stress_name)


    for entry in evaluation_data:
        session_id = entry.get("session_id")
        stress_after = entry.get("stress_after")

        if not session_id or not stress_after:
            continue

        if session_id in sessions_by_id:
            session = sessions_by_id[session_id]
            choice = session.get("choice")
            duration = session.get("duration")

            if not choice or not duration:
                continue

            if choice not in exercise_data:
                continue

            if duration <= 60:
                dur_key = 60
            elif duration <= 180:
                dur_key = 180
            else:
                dur_key = 300

            stress_name = stress_after.replace(".png", "")
            exercise_data[choice][dur_key]["after"].append(stress_name)

    return exercise_data
    



def create_statistics_image(exercise_data, output_dir):


    fig = plt.figure(figsize=(22, 34))  
    ax = fig.add_subplot(111)
    ax.axis('off')

    y_pos = 0.98
    line_height = 0.028
    small_line = 0.022

    
    ax.text(0.5, y_pos, "STATISTIK - AUSWERTUNG NEFFY ATEMERKENNUNG", fontsize=26, fontweight='bold',
            ha='center', va='top', transform=ax.transAxes)
    y_pos -= 0.045



    #total Number
    total_sessions = 0
    total_before = defaultdict(int)
    total_after = defaultdict(int)
    total_duration = {60: 0, 180: 0, 300: 0}
    exercise_count = {}

    for exercise in EXERCISE_NAMES.keys():
        exercise_count[exercise] = 0
        for dur in [60, 180, 300]:
            data = exercise_data.get(exercise, {}).get(dur, {})
            before_list = data.get("before", [])
            after_list = data.get("after", [])

            count = min(len(before_list), len(after_list))
            if count > 0:
                exercise_count[exercise] += count
                total_duration[dur] += count
                total_sessions += count

                for stress in before_list:
                    total_before[stress] += 1
                for stress in after_list:
                    total_after[stress] += 1

    ax.text(0.05, y_pos, f"TOTALE ANZAHL DOKUMENTIERTER ÜBUNGEN: {total_sessions}",
            fontsize=16, fontweight='bold', va='top')
    y_pos -= 0.035


     #Dauerverteilung komplett
    ax.text(0.05, y_pos, "TOTALE DAUERVERTEILUNG:", fontsize=14, fontweight='bold', va='top')
    y_pos -= 0.025

    for dur in [60, 180, 300]:
        name = DURATION_NAMES.get(dur, f"{dur}s")
        count = total_duration.get(dur, 0)
        pct = round(count / total_sessions * 100, 1) if total_sessions > 0 else 0
        ax.text(0.08, y_pos, f"  {name}: {count} ({pct}%)", fontsize=12, va='top')
        y_pos -= 0.022

    y_pos -= 0.015


 
     #totale Bewertungen vorher
    ax.text(0.05, y_pos, "TOTALE BEWERTUNGEN (VORHER):", fontsize=14, fontweight='bold', va='top')
    y_pos -= 0.025

    before_str = ", ".join([f"{k}: {v}" for k, v in total_before.items() if v > 0])
    ax.text(0.08, y_pos, f"  {before_str if before_str else 'keine'}", fontsize=12, va='top')
    y_pos -= 0.025




    #totale Bewertungen nachhar
    ax.text(0.05, y_pos, "TOTALE BEWERTUNGEN (NACHHER):", fontsize=14, fontweight='bold', va='top')
    y_pos -= 0.025

    after_str = ", ".join([f"{k}: {v}" for k, v in total_after.items() if v > 0])
    ax.text(0.08, y_pos, f"  {after_str if after_str else 'keine'}", fontsize=12, va='top')
    y_pos -= 0.03

      
      
    for exercise_key, exercise_name in EXERCISE_NAMES.items():
        y_pos = create_exercise_section(ax, exercise_key, exercise_name, exercise_data, y_pos)




    y_pos = 0.02
    ax.text(0.05, y_pos, "LEGENDE:", fontsize=12, fontweight='bold', va='bottom')
    y_pos += 0.018

    ax.text(0.08, y_pos, "Stress-Level (absteigend): Sehr entspannt > Entspannt > Mittel > Etwas gestresst > Gestresst > Keine Angaben",
            fontsize=10, va='bottom')

    plt.tight_layout()
    filepath = os.path.join(output_dir, "statistics.png")
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"Saved: {filepath}")
    return filepath


def create_exercise_section(ax, exercise_key, exercise_name, exercise_data, y_pos):
     #creates section for every added exercise
    has_data = False
    for dur in [60, 180, 300]:
        data = exercise_data.get(exercise_key, {}).get(dur, {})
        if data.get("before", []) or data.get("after", []):
            has_data = True
            break

    if not has_data:
        return y_pos

    #exercise name
    ax.text(0.05, y_pos, f"{exercise_name.upper()}:", fontsize=15, fontweight='bold', va='top')
    y_pos -= 0.028



     #total number of choicse for very exercise
    total_ex = 0
    for dur in [60, 180, 300]:
        data = exercise_data.get(exercise_key, {}).get(dur, {})
        count = min(len(data.get("before", [])), len(data.get("after", [])))
        total_ex += count

    ax.text(0.08, y_pos, f"  Anzahl gewählt: {total_ex}", fontsize=13, va='top')
    y_pos -= 0.022



     #durations
    dur_str = []
    for dur in [60, 180, 300]:
        data = exercise_data.get(exercise_key, {}).get(dur, {})
        count = min(len(data.get("before", [])), len(data.get("after", [])))
        if count > 0:
            name = DURATION_NAMES.get(dur, f"{dur}s")
            pct = round(count / total_ex * 100, 1) if total_ex > 0 else 0
            dur_str.append(f"{name}: {count} ({pct}%)")
            


    ax.text(0.08, y_pos, f"  Dauer: {', '.join(dur_str) if dur_str else 'keine'}", fontsize=12, va='top')
    y_pos -= 0.022



     #evaluations before
    before_dict = defaultdict(int)
    for dur in [60, 180, 300]:
        data = exercise_data.get(exercise_key, {}).get(dur, {})
        for stress in data.get("before", []):
            before_dict[stress] += 1

    before_str = ", ".join([f"{k}: {v}" for k, v in before_dict.items() if v > 0])
    ax.text(0.08, y_pos, f"  Bewertungen VORHER: {before_str if before_str else 'keine'}", fontsize=12, va='top')
    y_pos -= 0.022



     #evaluations after
    after_dict = defaultdict(int)
    for dur in [60, 180, 300]:
        data = exercise_data.get(exercise_key, {}).get(dur, {})
        for stress in data.get("after", []):
            after_dict[stress] += 1

    after_str = ", ".join([f"{k}: {v}" for k, v in after_dict.items() if v > 0])
    ax.text(0.08, y_pos, f"  Bewertungen NACHHER: {after_str if after_str else 'keine'}", fontsize=12, va='top')
    y_pos -= 0.03

    return y_pos


def main():
    session_path = os.path.join(LOG_DIR, "session_log.json")
    evaluation_path = os.path.join(LOG_DIR, "evaluation_log.json")

    session_data = load_json(session_path)
    evaluation_data = load_json(evaluation_path)

    print(f"Sessions geladen: {len(session_data)}")
    print(f"Evaluations geladen: {len(evaluation_data)}")

    # Debug: Zeige alle vorkommenden choice-Werte
    choices_in_log = set()
    for entry in session_data:
        c = entry.get("choice")
        if c:
            choices_in_log.add(c)
    print(f"Übungen im Log gefunden: {choices_in_log}")

    exercise_data = build_exercise_data(session_data, evaluation_data)

    create_statistics_image(exercise_data, OUTPUT_DIR)

    print(f"\nStatistik wurde gespeichert in: {os.path.join(OUTPUT_DIR, 'statistics.png')}")


if __name__ == "__main__":
    main()
