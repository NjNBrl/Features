# file: midi_caption_pipeline.py
import pretty_midi
import music21
import numpy as np
import json
from collections import Counter
import subprocess
import os

# ---------- Helpers ----------
GM_PROGRAMS = {0: "Acoustic Grand Piano", 25: "Acoustic Guitar (nylon)", 40: "Violin", 32: "Acoustic Bass", 73: "Flute"}
# (you can expand)

def synthesize_midi_to_wav(midi_path, wav_out, soundfont_path=None):
    """
    Optional: uses fluidsynth if installed. If not available, skip audio features.
    """
    if soundfont_path is None:
        raise ValueError("Provide soundfont (.sf2) path or skip audio synthesis")
    cmd = ["fluidsynth", "-ni", soundfont_path, midi_path, "-F", wav_out, "-r", "22050"]
    subprocess.run(cmd, check=True)

def top_instruments(pm: pretty_midi.PrettyMIDI, top_n=3):
    progs = []
    for inst in pm.instruments:
        if inst.is_drum: 
            progs.append("Drums")
        else:
            progs.append(inst.program)
    if not progs:
        return []
    counts = Counter(progs)
    top = [p for p,_ in counts.most_common(top_n)]
    # Map to names where possible
    names = []
    for p in top:
        if p == "Drums":
            names.append("Drums")
        else:
            names.append(pretty_midi.program_to_instrument_name(p))
    return names

# ---------- Improved chord extraction (no pm.get_notes) ----------
def guess_chord_from_pitch_classes(pcs):
    """
    pcs: set of pitch classes (ints 0..11)
    Returns a simple chord name like 'C', 'Am', 'Gdim', or a fallback 'C-E-G' style.
    """
    if not pcs:
        return None
    triads = {
        'maj': {0, 4, 7},
        'min': {0, 3, 7},
        'dim': {0, 3, 6},
        'aug': {0, 4, 8},
    }
    note_name = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

    # Try every possible root and see if a triad pattern is present
    for root in range(12):
        trans = set(((p - root) % 12) for p in pcs)
        for quality, pattern in triads.items():
            if pattern.issubset(trans):
                base = note_name[root]
                if quality == 'maj':
                    return f"{base}"
                elif quality == 'min':
                    return f"{base}m"
                else:
                    return f"{base}{quality}"
    # fallback: return pitch-class names sorted
    return "-".join(sorted(note_name[p] for p in pcs))

def extract_chords(pm: pretty_midi.PrettyMIDI, resolution=0.5, max_chords=40):
    """
    Naive chord sequence extraction:
      - quantize time into steps of `resolution` seconds
      - find notes overlapping each time window by checking note.start/note.end
      - produce a simple chord label per window using triad heuristics
    """
    end_time = pm.get_end_time()
    if end_time <= 0:
        return []

    times = np.arange(0.0, end_time, resolution)
    chords = []
    for t in times:
        active_pcs = set()
        for inst in pm.instruments:
            for n in inst.notes:
                # note overlaps the window [t, t+resolution)
                if n.start < (t + resolution) and n.end > t:
                    active_pcs.add(n.pitch % 12)
        if not active_pcs:
            continue
        chord_label = guess_chord_from_pitch_classes(active_pcs)
        if chord_label is None:
            continue
        # compress repeated consecutive identical chords later
        chords.append(chord_label)

    # compress consecutive repeats
    comp = []
    for ch in chords:
        if not comp or comp[-1] != ch:
            comp.append(ch)
    return comp[:max_chords]

def extract_basic_features(midi_path):
    pm = pretty_midi.PrettyMIDI(midi_path)
    tempo = pm.estimate_tempo()
    total_time = pm.get_end_time()
    num_tracks = len(pm.instruments)
    top_instr = top_instruments(pm, top_n=3)
    # pitch range
    pitches = []
    for inst in pm.instruments:
        for n in inst.notes:
            pitches.append(n.pitch)
    if pitches:
        pitch_min, pitch_max = min(pitches), max(pitches)
        pitch_range = pitch_max - pitch_min
    else:
        pitch_min = pitch_max = pitch_range = None

    # Note density
    if total_time > 0:
        note_density = len(pitches) / total_time
    else:
        note_density = 0.0

    chords = extract_chords(pm)


    features = {
        "tempo_bpm": round(float(tempo)),
        "duration_s": round(float(total_time), 2),
        "num_tracks": num_tracks,
        "top_instruments": top_instr,
        "pitch_min_midi": pitch_min,
        "pitch_max_midi": pitch_max,
        "pitch_range": pitch_range,
        "note_density_per_s": round(float(note_density), 3),
        "chord_sequence": chords,
    }
    return features

def features_to_text_summary(features):
    """Small deterministic single-paragraph summary for the LLM prompt."""
    parts = []
    parts.append(f"Tempo: {features.get('tempo_bpm', 'unknown')} BPM")
    parts.append(f"Duration: {features.get('duration_s', 'unknown')}s")
    parts.append(f"Tracks: {features.get('num_tracks', 'unknown')}")
    instr = features.get('top_instruments', [])
    if instr:
        parts.append("Instruments: " + ", ".join(instr))
    if features.get('pitch_min_midi') is not None:
        parts.append(f"Pitch range: MIDI {features['pitch_min_midi']}-{features['pitch_max_midi']}")
    parts.append(f"Note density: {features.get('note_density_per_s', 0)} notes/s")
    chords = features.get('chord_sequence', [])
    if chords:
        parts.append("Chord progression (sample): " + "; ".join(chords[:6]))
    return " | ".join(parts)

# ---------- Example usage ----------
if __name__ == "__main__":
    midi_folder = "1.Midi"
    output_folder = "2A.Midi_summaries"
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(midi_folder):
        if filename.lower().endswith(".mid"):
            midi_path = os.path.join(midi_folder, filename)
            print(f"🎵 Processing {filename}...")

            try:
                feats = extract_basic_features(midi_path)

                # Create summary text
                summary_line = f"Summary: {features_to_text_summary(feats)}"
                print(summary_line)  # Print to console

                # Save summary to .txt file
                txt_filename = os.path.splitext(filename)[0] + "_summary.txt"
                txt_path = os.path.join(output_folder, txt_filename)
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(summary_line)

                print(f"✅ Summary saved to {txt_path}\n")

            except Exception as e:
                print(f"❌ Failed to process {filename}: {e}\n")

