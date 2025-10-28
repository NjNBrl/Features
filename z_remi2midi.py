from miditok import REMI, TokenizerConfig
from pathlib import Path

# ---------- SAME CONFIG used during encoding ---------- #
config = TokenizerConfig(
    beat_res={(0, 4): 8},
    use_chords=True,
    use_programs=True,
    use_tempos=True,
    use_time_signatures=True,
    use_sustain_pedals=True,
    use_pitch_intervals=False,
    use_tracks=True,
    num_velocities=32,
    program_changes=True,
)

# Initialize tokenizer
tokenizer = REMI(config)

def convert_remi_to_midi(input_txt_path: str, output_midi_path: str):
    txt_path = Path(input_txt_path)
    with open(txt_path, "r", encoding="utf-8") as f:
        tokens = f.read().split()

    midi_obj = tokenizer.tokens_to_midi(tokens)
    midi_obj.dump_midi(output_midi_path)
    print(f"✅ MIDI saved: {output_midi_path}")

def batch_convert_folder(input_folder="7.REMI", output_folder="MIDI_CHECK"):
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(exist_ok=True)

    txt_files = list(input_path.glob("*.txt"))
    if not txt_files:
        print(f"⚠️ No REMI .txt files found in {input_folder}")
        return

    for i, txt_file in enumerate(txt_files, 1):
        print(f"[{i}/{len(txt_files)}] Processing {txt_file.name} ...")
        output_file = output_path / f"{txt_file.stem}.mid"
        convert_remi_to_midi(txt_file, output_file)

    print(f"\n🎵 All MIDIs reconstructed in: {output_folder}")

if __name__ == "__main__":
    batch_convert_folder("7.REMI1", "MIDI_CHECK1")


