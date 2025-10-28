from miditok import REMI, TokenizerConfig
from pathlib import Path

# ------------------ CONFIGURATION ------------------ #
# This configuration ensures reversibility and multi-instrument support
config = TokenizerConfig(
    beat_res={(0, 4): 8},           # 1/8 beat resolution for all bars (fine enough)
    use_chords=True,                # optional, helps for tonal tasks
    use_programs=True,              # ✅ retain instrument program numbers
    use_tempos=True,                # ✅ preserve tempo changes
    use_time_signatures=True,       # ✅ preserve time signatures
    use_sustain_pedals=True,        # sustain pedal control
    use_pitch_intervals=False,      # absolute pitches (more standard)
    use_tracks=True,                # ✅ multi-track tokenization
    num_velocities=32,              # velocity bins
    program_changes=True,           # include program tokens
)

# Initialize tokenizer
tokenizer = REMI(config)


def convert_midi_to_remi(input_midi_path: str, output_txt_path: str):
    """
    Converts a MIDI file into REMI tokens (multi-instrument, consistent timing)
    and saves them to a .txt file.
    """
    midi_path = Path(input_midi_path)
    try:
        # Tokenize MIDI
        tokenized = tokenizer(midi_path)

        # Handle multi-track or single-track cases
        if isinstance(tokenized, list):
            tokens = [token for seq in tokenized for token in seq.tokens]
        else:
            tokens = tokenized.tokens

        # Save tokens as plain text
        with open(output_txt_path, "w", encoding="utf-8") as f:
            f.write(" ".join(tokens))

        print(f"✅ Converted: {input_midi_path.name} → {output_txt_path.name}")

    except Exception as e:
        print(f"❌ Error processing {input_midi_path.name}: {e}")


def batch_convert_folder(input_folder="1.Midi", output_folder="7.REMI"):
    """
    Converts all .mid files in the input folder to REMI .txt files.
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(exist_ok=True)

    midi_files = list(input_path.glob("*.mid"))
    if not midi_files:
        print(f"⚠️ No MIDI files found in {input_folder}")
        return

    for midi_file in midi_files:
        output_file = output_path / f"{midi_file.stem}.txt"
        convert_midi_to_remi(midi_file, output_file)

    print(f"\n🎵 All MIDIs converted and saved in: {output_folder}")


# ------------------ MAIN ------------------ #
if __name__ == "__main__":
    batch_convert_folder("1.Midi", "7.REMI")idi_file, output_file)
