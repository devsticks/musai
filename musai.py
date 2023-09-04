import tensorflow as tf
import numpy as np

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH

import sounddevice as sd
from scipy.io.wavfile import write
import pretty_midi

basic_pitch_model = tf.saved_model.load(str(ICASSP_2022_MODEL_PATH))

# Define the notes for major and minor chords
major_chord_notes = [0, 4, 7]
minor_chord_notes = [0, 3, 7]
diminished_chord_notes = [0, 3, 6]
augmented_chord_notes = [0, 4, 8]
sus2_chord_notes = [0, 2, 7]
sus4_chord_notes = [0, 5, 7]
minor7_chord_notes = [0, 3, 7, 10]
major7_chord_notes = [0, 4, 7, 11] # same as 1/3. Need to analyse what the bass note is
dominant7_chord_notes = [0, 4, 7, 10]

# guitar chords often have the root and fifth in them - need to account for this
minoradd4add7_chord_notes = [0, 3, 5, 7, 10]

# Define the notes for major keys
P1_chord_notes = [0, 4, 7]
m2_chord_notes = [2, 5, 9]
M2_chord_notes = [2, 6, 9]
m3_chord_notes = [4, 7, 11]
m3over1_chord_notes = [4, 7, 0]
M3_chord_notes = [4, 8, 11]
P4_chord_notes = [5, 9, 0]
P5_chord_notes = [7, 11, 2]
m6_chord_notes = [9, 0, 4]
m7_chord_notes = [11, 2, 6]
m7over5_chord_notes = [11, 2, 7]

major_scale_intervals = [2, 2, 1, 2, 2, 2, 1]
major_scale_notes = [0, 2, 4, 5, 7, 9, 11]

def calculate_chord(notes, key = None):
    # Sort the notes in ascending order
    notes.sort()

    # Iterate through each note as a potential root note
    for i in range(len(notes)):
        scale_intervals = []
        subnotes = []
        for j in range(len(notes)):
            scale_note = notes[(i + j) % len(notes)] - notes[i]
            # limit to a range of 0-12
            scale_note = scale_note % 12
            scale_intervals.append(scale_note)
            subnotes.append(notes[(i + j) % len(notes)])

        scale_intervals = np.array(scale_intervals)
        # scale_intervals = np.unique(scale_intervals)
        subnotes = np.array(subnotes)
        # subnotes = np.unique(subnotes)
        print(scale_intervals)
        # print the actual notes
        print([pretty_midi.note_number_to_name(note) for note in subnotes])

        # Determine the chord type based on scale notes
        if set(scale_intervals).issubset(set(major_chord_notes)):
        # if scale_intervals in major_chord_notes:
            chord_type = "Major"
        elif set(scale_intervals).issubset(set(minor_chord_notes)):
            chord_type = "Minor"
        elif set(scale_intervals).issubset(set(diminished_chord_notes)):
            chord_type = "Diminished"
        elif set(scale_intervals).issubset(set(augmented_chord_notes)):
            chord_type = "Augmented"
        elif set(scale_intervals).issubset(set(sus2_chord_notes)) or set(scale_intervals).issubset(set(sus2_chord_notes).union(set(major_chord_notes))):
            chord_type = "Sus2"
        elif set(scale_intervals).issubset(set(sus4_chord_notes)) or set(scale_intervals).issubset(set(sus4_chord_notes).union(set(major_chord_notes))):
            chord_type = "Sus4"
        elif set(scale_intervals).issubset(set(minor7_chord_notes)):
            chord_type = "Minor7"
        elif set(scale_intervals).issubset(set(major7_chord_notes)):
            chord_type = "Major7"
        elif set(scale_intervals).issubset(set(dominant7_chord_notes)):
            chord_type = "Dominant7"
        elif set(scale_intervals).issubset(set(minoradd4add7_chord_notes)):
            chord_type = "MinorAdd4Add7"
        else:
            chord_type = "Unknown"

        # Determine the root note of the chord
        root_note = notes[i]

        if chord_type != "Unknown":
            break

    if key is not None:
        return interval_to_nashville_number(root_note - key), chord_type
    else:
        return f"{pretty_midi.note_number_to_name(root_note)} {chord_type}"

def interval_to_nashville_number(interval):
    # return the index of the interval in the major scale
    interval = interval % 12
    print(f"Bass note interval: {interval}")
    return major_scale_notes.index(interval)

# def interval_to_nashville_number(interval):
#     # Define the notes for major keys
#     P1_chord_notes = [0, 4, 7]
#     m2_chord_notes = [2, 5, 9]
#     M2_chord_notes = [2, 6, 9]
#     m3_chord_notes = [4, 7, 11]
#     m3over1_chord_notes = [4, 7, 0]
#     M3_chord_notes = [4, 8, 11]
#     P4_chord_notes = [5, 9, 0]
#     P5_chord_notes = [7, 11, 2]
#     m6_chord_notes = [9, 0, 4]
#     m7_chord_notes = [11, 2, 6]
#     m7over5_chord_notes = [11, 2, 7]

#     # Determine the chord type based on scale notes
#     if interval in P1_chord_notes:
#         chord_number = "1"
#     elif interval in m2_chord_notes:
#         chord_number = "b2"
#     elif interval in M2_chord_notes:
#         chord_number = "2"
#     elif interval in m3_chord_notes:
#         chord_number = "b3"
#     elif interval in m3over1_chord_notes:
#         chord_number = "b3"
#     elif interval in M3_chord_notes:
#         chord_number = "3"
#     elif interval in P4_chord_notes:
#         chord_number = "4"
#     elif interval in P5_chord_notes:
#         chord_number = "5"
#     elif interval in m6_chord_notes:
#         chord_number = "b6"
#     elif interval in m7_chord_notes:
#         chord_number = "b7"
#     elif interval in m7over5_chord_notes:
#         chord_number = "b7"
#     else:
#         chord_number = "Unknown"

#     return chord_number

def calculate_chord_type(notes, key, bass_note):
    # Sort the notes in ascending order
    notes.sort()

    remove_one = False

    while True:
        scale_intervals = []
        subnotes = []
        for j in range(len(notes)):
            scale_note = notes[(j) % len(notes)] - bass_note
            # limit to a range of 0-12
            scale_note = scale_note % 12
            # don't add the 1st or the 5th note of the key (which are ambiguous)
            if remove_one and (notes[j]-key)%12 in [0]:
                continue
            # if remove_one_and_five:
            #     scale_note = scale_note + key - notes[i] # make the scale note relative to the chord root note
            #     scale_note = scale_note % 12
            scale_intervals.append(scale_note)
            subnotes.append(notes[(j) % len(notes)])

        scale_intervals = np.array(scale_intervals)
        # scale_intervals = np.unique(scale_intervals)
        subnotes = np.array(subnotes)
        # subnotes = np.unique(subnotes)
        print(scale_intervals)
        # print the actual notes
        print([pretty_midi.note_number_to_name(note) for note in subnotes])

        # Determine the chord type based on scale notes
        if set(scale_intervals).issubset(set(major_chord_notes)):
        # if scale_intervals in major_chord_notes:
            chord_type = "Major"
        elif set(scale_intervals).issubset(set(minor_chord_notes)):
            chord_type = "Minor"
        elif set(scale_intervals).issubset(set(diminished_chord_notes)):
            chord_type = "Diminished"
        elif set(scale_intervals).issubset(set(augmented_chord_notes)):
            chord_type = "Augmented"
        elif set(scale_intervals).issubset(set(sus2_chord_notes)) or set(scale_intervals).issubset(set(sus2_chord_notes).union(set(major_chord_notes))):
            chord_type = "Sus2"
        elif set(scale_intervals).issubset(set(sus4_chord_notes)) or set(scale_intervals).issubset(set(sus4_chord_notes).union(set(major_chord_notes))):
            chord_type = "Sus4"
        elif set(scale_intervals).issubset(set(minor7_chord_notes)):
            chord_type = "Minor7"
        elif set(scale_intervals).issubset(set(major7_chord_notes)):
            chord_type = "Major7"
        elif set(scale_intervals).issubset(set(dominant7_chord_notes)):
            chord_type = "Dominant7"
        elif set(scale_intervals).issubset(set(minoradd4add7_chord_notes)):
            chord_type = "MinorAdd4Add7"
        else:
            chord_type = "Unknown"

        # if chord_type != "Unknown":
        #     break
        
        if chord_type != "Unknown" or remove_one:
            break
        else:
            remove_one = True

    return chord_type

'''Given a key and a set of notes, determine the chord relative to the key.
Returns the zero-indexed chord number and the chord type.'''
def calculate_relative_chord(notes, key, use_bass_note=True):
    # Sort the notes in ascending order
    notes.sort()

    if use_bass_note:
        # Determine the bass note of the chord
        bass_note = notes[0]
        print(f"Bass note: {pretty_midi.note_number_to_name(bass_note)}")
        try: 
            bass_note_interval = bass_note - key
            chord_number = interval_to_nashville_number(bass_note_interval)
            print(f"Chord number in key: {chord_number + 1}")
            chord_type = calculate_chord_type(notes, key, bass_note)
        except: 
            chord_number = None
            chord_type = None
    
    if not use_bass_note or chord_type == "Unknown" or chord_number is None:
        bass_note = None
        print()
        print("Trying without bass note")

        # not tested from here:
        # example, given [C#3, F#4, A4] and key of D, determine that it's a minor chord, and the bass note is F#4, which is the iii chord.

        # Iterate through each note as a potential chord root note to determine the chord relative to the key root note
        # Assume it's fine if the scale's 1st or 5th are added or removed

        chord_number, chord_type = calculate_chord(notes, key)

        # for i in range(len(notes)):
        #     intervals_from_root = []
        #     subnotes = []
        #     for j in range(len(notes)):
        #         scale_note = notes[(i + j) % len(notes)] - notes[i]
        #         # limit to a range of 0-12
        #         scale_note = scale_note % 12
        #         intervals_from_root.append(scale_note)
        #         subnotes.append(notes[(i + j) % len(notes)])

        #     intervals_from_root = np.array(intervals_from_root)
        #     # intervals_from_root = np.unique(intervals_from_root)
        #     subnotes = np.array(subnotes)
        #     # subnotes = np.unique(subnotes)
        #     print(intervals_from_root)
        #     # print the actual notes
        #     print([pretty_midi.note_number_to_name(note) for note in subnotes])

        #     # Determine the chord number based on the intervals from the root note
        #     # allowing flexibility for the 1st and 5th notes in the key to be added or removed


    return chord_number, chord_type

def determine_major_scale(notes):
    # Sort the notes in ascending order
    notes.sort()

    # Define the intervals for major scales
    # major_scale_intervals = [2, 2, 1, 2, 2, 2, 1]
    major_scale_intervals = [0, 2, 4, 5, 7, 9, 11]

    # Iterate through each note as a potential chord root note
    for i in range(len(notes)):
        scale_intervals = []
        for j in range(len(notes)):
            scale_note = notes[(i + j) % len(notes)] - notes[i]
            # limit to a range of 0-12
            scale_note = scale_note % 12
            scale_intervals.append(scale_note)

        print(scale_intervals)

        # Check if the intervals are a subset of the major scale pattern
        if set(scale_intervals).issubset(set(major_scale_intervals)):
        # if scale_intervals == major_scale_intervals:
            root_note = notes[i] # need to allow for ambiguity
            scale_name = f"{pretty_midi.note_number_to_name(root_note)} Major"
            return scale_name

    return "Unknown"

# E major scale starting from E
# notes = [64, 66, 68, 69, 71, 73, 75]
# notes of E major triad, starting from B
# notes = [59, 64, 68, 71]

# scale_name = determine_major_scale(notes)
# print(f"The scale is: {scale_name}")

# notes of D major in DADGAD tuning
notenames = ["D2", "A2", "D3", "A3", "A3", "D4"]
notes = [pretty_midi.note_name_to_number(notename) for notename in notenames]
chord_name, chord_type = calculate_relative_chord(notes, 62)
print(f"(D) The chord is: {chord_name+1} {chord_type}")

# notes of E chord in DADGAD tuning
notenames = ["E2", "B2", "D3", "G3", "A3", "D4"]
notes = [pretty_midi.note_name_to_number(notename) for notename in notenames]
chord_name, chord_type = calculate_relative_chord(notes, 62)
print(f"(E) The chord is: {chord_name+1} {chord_type}")

# notes of F# chord in DADGAD tuning
notenames = ["C#2", "F#2", "D3", "A3", "A3", "D4"]
notes = [pretty_midi.note_name_to_number(notename) for notename in notenames]
chord_name, chord_type = calculate_relative_chord(notes, 62)
print(f"(F#) The chord is: {chord_name+1} {chord_type}")

# notes of G chord in DADGAD tuning
notenames = ["G2", "D3", "D3", "G3", "A3", "D4"]
notes = [pretty_midi.note_name_to_number(notename) for notename in notenames]
chord_name, chord_type = calculate_relative_chord(notes, 62)
print(f"(G) The chord is: {chord_name+1} {chord_type}")

# notes of A chord in DADGAD tuning
notenames = ["A2", "E3", "D3", "A3", "A3", "D4"]
notes = [pretty_midi.note_name_to_number(notename) for notename in notenames]
chord_name, chord_type = calculate_relative_chord(notes, 62)
print(f"(A) The chord is: {chord_name+1} {chord_type}")

# notes of B chord in DADGAD tuning
notenames = ["B2", "F#3", "D3", "B3", "A3", "D4"]
notes = [pretty_midi.note_name_to_number(notename) for notename in notenames]
chord_name, chord_type = calculate_relative_chord(notes, 62)
print(f"(B) The chord is: {chord_name+1} {chord_type}")


# def determine_major_scale(notes):
#     # Sort the notes in ascending order
#     notes.sort()

#     # Define the intervals for major scales
#     major_scale_intervals = [2, 2, 1, 2, 2, 2, 1]

#     # Check all possible starting notes within the set of notes
#     for i in range(len(notes)):
#         # Calculate the intervals between consecutive notes starting from i
#         intervals = [(notes[(i + j + 1) % len(notes)] - notes[(i + j) % len(notes)]) for j in range(len(notes) - 1)]
#         print(intervals)

#         # Check if the intervals match any major scale
#         if intervals == major_scale_intervals:
#             root_note = notes[i]
#             scale_name = f"{pretty_midi.note_number_to_name(root_note)} Major"
#             return scale_name

#     return "Unknown"

# # Example set of notes (replace this with your own list of note numbers)
# notes = [62, 64, 65, 67, 69, 71, 72]  # D major scale starting from D

# scale_name = determine_major_scale(notes)
# print(f"The scale is: {scale_name}")

# exit()

while True:
    fs = 44100  # Sample rate
    seconds = 1  # Duration of recording

    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1) # try overlapping recordings?
    sd.wait()  # Wait until recording is finished
    write('output.wav', fs, myrecording)  # Save as WAV file 

    model_output, midi_data, note_events = predict(
        'output.wav',
        basic_pitch_model,
    )

    # Set the current time for analysis
    current_time = 0.0

    # Set the time window for chord analysis (in seconds)
    chord_window = 0.5

    # Iterate through the time points in the MIDI data
    while current_time < midi_data.get_end_time():
        # Get the notes that are being played within the current time window
        chord_notes = []
        for instrument in midi_data.instruments:
            for note in instrument.notes:
                if current_time <= note.start < current_time + chord_window:
                    chord_notes.append(note.pitch)

        # Determine the chord based on the notes being played
        if chord_notes:
            chord_notes = np.array(chord_notes)
            # Sort the notes to form the chord
            chord_notes.sort()

            if len(np.unique(chord_notes)) > 0:
                # chord_name = calculate_chord(chord_notes) 
                key = "E0"
                key = pretty_midi.note_name_to_number(key)
                chord_number, chord_type = calculate_relative_chord(chord_notes, key)
                if chord_number is not None:
                    chord_name = f"{chord_number+1} {chord_type}"
                else:
                    chord_name = "Unknown"
            else:
                chord_name = "Unknown"

            # # Print the chord
            # chord_name = pretty_midi.note_number_to_name(chord_notes[0])
            # for note in chord_notes[1:]:
            #     chord_name += "-" + pretty_midi.note_number_to_name(note)
            print(f"Chord at {current_time:.2f}s: {chord_name}")

        # Move to the next time window
        current_time += chord_window

# # Example set of notes (replace this with your own list of note numbers)
# notes = [60, 64, 67]  # C major triad

# chord_name = determine_chord(notes)
# print(f"The chord is: {chord_name}")
