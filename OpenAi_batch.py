from openai import OpenAI
import os

# --- 1. OpenAI API client ---
client = OpenAI(api_key="YOUR API KEY HERE")  # <-- your API key

# --- 2. Example pairs for GPT to learn the style ---
examples = """
You are a music caption generator. Given a MIDI feature summary, give me structured tag captions. Do not invent instruments.

FeatureSummary : Tempo: 203 BPM | Duration: 333.88s | Tracks: 4 | 
Instruments: Acoustic Grand Piano, String Ensemble 1, Pan Flute | 
Pitch range: MIDI 22-107 | Note density: 5.984 notes/s | 
Chord progression (sample): C#; C#-E; C#m; B-C#-E; B-E; B-E-F#

Caption: [EMOTION_SADNESS] [GENRE_SOUNDTRACK] [INSTRUMENT_PIANO] [INSTRUMENT_STRINGS] [INSTRUMENT_FLUTE] [KEY_C#_MINOR] [TEMPO_FAST]


FeatureSummary : Tempo: 233 BPM | Duration: 74.01s | Tracks: 6 | 
Instruments: Flute, Pad 3 (polysynth), String Ensemble 1 | 
Pitch range: MIDI 30-83 | Note density: 16.769 notes/s | 
Chord progression (sample): C#-E; C#-E-F#; A; B-C#-D#; B-C#; A

Caption: [EMOTION_JOY] [GENRE_POP] [INSTRUMENT_FLUTE] [INSTRUMENT_SYNTH] [INSTRUMENT_STRINGS] [KEY_C#_MINOR] [TEMPO_FAST]


FeatureSummary : Tempo: 184 BPM | Duration: 91.49s | Tracks: 1 | Instruments: Acoustic Grand Piano | 
Pitch range: MIDI 31-96 | Note density: 7.444 notes/s | 
Chord progression (sample): C; Cm; D#; Cm; Ddim; A#

Caption: [EMOTION_JOY] [GENRE_CLASSICAL] [INSTRUMENT_PIANO] [KEY_F_MINOR] [TEMPO_FAST]

"""

# --- 3. Paths ---
summary_folder = "2A.Midi_summaries"
output_folder = "3A.captions"
os.makedirs(output_folder, exist_ok=True)

# --- 4. Process all summaries ---
for filename in os.listdir(summary_folder):
    if filename.lower().endswith(".txt"):
        summary_path = os.path.join(summary_folder, filename)
        
        try:
            # Read the summary text
            with open(summary_path, "r", encoding="utf-8") as f:
                summary_text = f.read().strip()
            
            print(f"🎵 Processing {filename} ...")

            # Build the GPT prompt
            prompt = f"""{examples}

FeatureSummary: {summary_text}
Caption:"""

            # Call GPT
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.2
            )

            caption = response.choices[0].message.content.strip()
            print(f"Generated Caption: {caption}\n")

            # Save caption to file
            caption_filename = os.path.splitext(filename)[0] + "_caption.txt"
            caption_path = os.path.join(output_folder, caption_filename)
            with open(caption_path, "w", encoding="utf-8") as f:
                f.write(caption)

            print(f"✅ Caption saved to {caption_path}\n")

        except Exception as e:
            print(f"❌ Failed to process {filename}: {e}\n")



