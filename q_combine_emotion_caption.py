import os

folder_summary = '3A.captions'
folder_emotion = '5A.lyrics_emotion'
output_folder = '6A.emotin_labelled_caption'

# Make sure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Get list of files in both folders
summary_files = [f for f in os.listdir(folder_summary) if f.endswith('_summary_caption.txt')]
emotion_files = [f for f in os.listdir(folder_emotion) if f.endswith('_emotion.txt')]

# Extract base names from summary files (before _summary_caption)
summary_bases = {f.rsplit('_summary_caption.txt', 1)[0] for f in summary_files}
emotion_bases = {f.rsplit('_emotion.txt', 1)[0] for f in emotion_files}

# Find common base names
common_bases = summary_bases.intersection(emotion_bases)

for base in common_bases:
    summary_path = os.path.join(folder_summary, f'{base}_summary_caption.txt')
    emotion_path = os.path.join(folder_emotion, f'{base}_emotion.txt')

    # Read both files
    with open(summary_path, 'r', encoding='utf-8') as f_summary:
        summary_content = f_summary.read()
    with open(emotion_path, 'r', encoding='utf-8') as f_emotion:
        emotion_content = f_emotion.read()

    # Append contents (you can customize how to join them)
    combined_content = emotion_content + '\n'+ summary_content 

    # Save the combined content to output folder
    combined_path = os.path.join(output_folder, f'{base}_combined.txt')
    with open(combined_path, 'w', encoding='utf-8') as f_out:
        f_out.write(combined_content)

print(f"Combined files saved for {len(common_bases)} base names.")
