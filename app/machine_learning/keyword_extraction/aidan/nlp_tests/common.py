import os

current_dir = os.path.dirname(__file__)
summary_path = os.path.join(current_dir, 'sample_summary.txt')
full_text_path = os.path.join(current_dir, 'sample_full_text.txt')

def get_text():
    use_summary = input("Use summary text? (instead of full): ")
    use_summary = True if use_summary.lower() == "yes" else False
    file_path = summary_path if use_summary else full_text_path
    with open(file_path, 'r') as f:
        full_text = f.read()
    return full_text