import os
from pathlib import Path
from miditok import REMI  # Requires: pip install miditok

def convert_midi_to_remi(input_midi_path: str, output_txt_path: str):
    """
    Converts a MIDI file to REMI token representation and saves it as a TXT file.
    
    Args:
        input_midi_path (str): Path to the input MIDI file.
        output_txt_path (str): Path to save the output TXT file containing REMI tokens.
    """
    tokenizer = REMI()
    midi_path = Path(input_midi_path)

    try:
        # Load and tokenize
        tok_sequence = tokenizer(midi_path)

        # Handle single / multi-track
        if isinstance(tok_sequence, list):
            tokens = [token for seq in tok_sequence for token in seq.tokens]
        else:
            tokens = tok_sequence.tokens

        # Save tokens to TXT (space-separated or line-separated)
        with open(output_txt_path, "w") as f:
            f.write(" ".join(tokens))  # all tokens in one line
            # OR: for line-by-line
            # f.write("\n".join(tokens))

        print(f"✅ REMI tokens saved: {output_txt_path}")

    except Exception as e:
        print(f"❌ Error processing {input_midi_path}: {e}")


if __name__ == "__main__":
    input_folder = Path("1.Midi")
    output_folder = Path("7.REMI")
    output_folder.mkdir(exist_ok=True)  # Create folder if not exists

    # Process all .mid files in the folder
    for midi_file in input_folder.glob("*.mid"):
        output_file = output_folder / (midi_file.stem + ".txt")  # <-- save as .txt
        convert_midi_to_remi(midi_file, output_file)
