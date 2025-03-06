import sys

def split_jsonl_file(input_file, lines_per_file=10000):
    """
    Splits a JSONL file into multiple files with a given number of lines per file.
    
    Args:
        input_file (str): The path to the JSONL file.
        lines_per_file (int): Number of lines per output file (default is 10000).
    """
    file_count = 1
    current_lines = []
    
    with open(input_file, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            current_lines.append(line)
            # When we've reached the desired number of lines, write them out to a new file.
            if line_num % lines_per_file == 0:
                output_file = f"{input_file}_part{file_count}.jsonl"
                with open(output_file, "w", encoding="utf-8") as out_f:
                    out_f.writelines(current_lines)
                print(f"Created: {output_file} with {len(current_lines)} lines.")
                current_lines = []
                file_count += 1
                
        # Write any remaining lines to a final file
        if current_lines:
            output_file = f"{input_file}_part{file_count}.jsonl"
            with open(output_file, "w", encoding="utf-8") as out_f:
                out_f.writelines(current_lines)
            print(f"Created: {output_file} with {len(current_lines)} lines.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python split_jsonl.py <input_file> [lines_per_file]")
        sys.exit(1)
        
    input_file = sys.argv[1]
    # Optionally allow the user to specify a different number of lines per file
    lines_per_file = int(sys.argv[2]) if len(sys.argv) >= 3 else 10000
    
    split_jsonl_file(input_file, lines_per_file)
