import os
import pandas as pd
import mido
from mido import MidiFile, MidiTrack, Message, MetaMessage

def midi_to_csv(midi_file, csv_file):
    try:
        midi = MidiFile(midi_file)
        events = []

        for track in midi.tracks:
            for msg in track:
                if msg.type == 'sequencer_specific' or msg.type == 'end_of_track':
                    continue

                event = {
                    'time': msg.time,
                    'type': msg.type,
                }

                if msg.type == 'note_on' or msg.type == 'note_off':
                    event['channel'] = msg.channel
                    event['note'] = msg.note
                    event['velocity'] = msg.velocity
                elif msg.type == 'control_change':
                    event['channel'] = msg.channel
                    event['control'] = msg.control
                    event['value'] = msg.value
                elif msg.type == 'program_change':
                    event['channel'] = msg.channel
                    event['program'] = msg.program
                elif msg.type == 'pitchwheel':
                    event['channel'] = msg.channel
                    event['pitch'] = msg.pitch
                elif msg.type == 'sysex':
                    event['data'] = msg.data
                elif msg.type == 'meta':
                    event['type'] = 'meta'
                    event['subtype'] = msg.type
                    if msg.type == 'text':
                        event['text'] = msg.text
                    elif msg.type == 'track_name':
                        event['name'] = msg.name
                    elif msg.type == 'instrument_name':
                        event['name'] = msg.name
                    elif msg.type == 'key_signature':
                        event['key'] = msg.key
                        event['scale'] = msg.scale
                    elif msg.type == 'time_signature':
                        event['numerator'] = msg.numerator
                        event['denominator'] = msg.denominator
                        event['clocks_per_click'] = msg.clocks_per_click
                        event['notated_32nd_notes_per_beat'] = msg.notated_32nd_notes_per_beat
                    elif msg.type == 'set_tempo':
                        event['tempo'] = msg.tempo

                events.append(event)

        df = pd.DataFrame(events)
        df.to_csv(csv_file, index=False)
        print(f"Converted {midi_file} to {csv_file}")
    except Exception as e:
        print(f"Error converting {midi_file} to {csv_file}: {e}")

def csv_to_midi(csv_file, midi_file):
    try:
        df = pd.read_csv(csv_file)
        midi = MidiFile()
        track = MidiTrack()
        midi.tracks.append(track)

        # Initialize the accumulated time
        accumulated_time = 0

        for index, row in df.iterrows():
            msg_type = row['type']
            if msg_type == 'sequencer_specific' or msg_type == 'end_of_track':
                continue

            msg_kwargs = {
                # Accumulate the relative time to get the absolute time
                'time': row['time'] + accumulated_time,
            }

            # Update the accumulated time with the current relative time
            accumulated_time += row['time']


            if 'channel' in df.columns and pd.notnull(row['channel']):
                msg_kwargs['channel'] = int(row['channel'])

            if 'note' in df.columns and pd.notnull(row['note']):
                msg_kwargs['note'] = int(row['note'])

            if 'velocity' in df.columns and pd.notnull(row['velocity']):
                msg_kwargs['velocity'] = int(row['velocity'])

            if 'control' in df.columns and pd.notnull(row['control']):
                msg_kwargs['control'] = int(row['control'])

            if 'value' in df.columns and pd.notnull(row['value']):
                msg_kwargs['value'] = int(row['value'])

            if 'program' in df.columns and pd.notnull(row['program']):
                msg_kwargs['program'] = int(row['program'])

            if 'pitch' in df.columns and pd.notnull(row['pitch']):
                msg_kwargs['pitch'] = int(row['pitch'])

            if 'data' in df.columns and pd.notnull(row['data']):
                msg_kwargs['data'] = [int(x.strip()) for x in row['data'].strip('[]').split(',')]

            if 'subtype' in df.columns and pd.notnull(row['subtype']):
                msg_type = row['subtype']

            if msg_type == 'meta':
                if 'text' in df.columns and pd.notnull(row['text']):
                    msg = MetaMessage('text', text=row['text'], **msg_kwargs)
                elif 'name' in df.columns and pd.notnull(row['name']):
                    msg = MetaMessage('track_name', name=row['name'], **msg_kwargs)
                elif 'key' in df.columns and pd.notnull(row['key']):
                    msg = MetaMessage('key_signature', key=row['key'], scale=row['scale'], **msg_kwargs)
                elif 'numerator' in df.columns and pd.notnull(row['numerator']):
                    msg = MetaMessage('time_signature', numerator=row['numerator'], 
                        denominator=row['denominator'],
                        clocks_per_click=row['clocks_per_click'], 
                        notated_32nd_notes_per_beat=row['notated_32nd_notes_per_beat'], 
                        **msg_kwargs)
                elif 'tempo' in df.columns and pd.notnull(row['tempo']):
                    msg = MetaMessage('set_tempo', tempo=row['tempo'], **msg_kwargs)
                else:
                    msg = MetaMessage(msg_type, **msg_kwargs)
            elif msg_type == 'sysex':
                msg = Message('sysex', **msg_kwargs)
            else:
                msg = Message(msg_type, **msg_kwargs)

            track.append(msg)

        midi.save(midi_file)
        print(f"Converted {csv_file} to {midi_file}")
    except Exception as e:
        print(f"Error converting {csv_file} to {midi_file}: {e}")

def main():
    # Prompt the user to enter a file name
    file_name = input("Enter the file name: ")
    # Split the file name into base name and extension
    base_name, extension = os.path.splitext(file_name)

    # Check the file extension and call the appropriate conversion function
    if extension == '.mid':
        csv_file = base_name + '.csv'
        midi_to_csv(file_name, csv_file)
    elif extension == '.csv':
        midi_file = base_name + '.mid'
        csv_to_midi(file_name, midi_file)
    else:
        print("Unsupported file extension. Please provide a .mid or .csv file.")

if __name__ == "__main__":
    main()
