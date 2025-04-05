import csv
import re

def fix_csv_format(input_file, output_file):
    # Define the expected column headers
    expected_headers = [
        "タイトル", "ステータス", "URL", "説明", "期間", "金額", 
        "セクション", "選択した項目"
    ]
    
    # Read the input CSV
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # First, fix the most common issue - commas in the text fields breaking CSV structure
    # We'll process the content line by line
    lines = content.split('\n')
    header = lines[0]
    
    fixed_lines = [header]
    
    for i in range(1, len(lines)):
        if not lines[i].strip():  # Skip empty lines
            continue
            
        # Split the line
        parts = lines[i].split(',')
        
        # If we have the expected number of fields or fewer, add as is
        if len(parts) <= len(expected_headers):
            fixed_lines.append(lines[i])
            continue
            
        # We have too many commas - need to fix
        title = parts[0]
        status = parts[1]
        url = parts[2]
        
        # Find where the explanation field should end
        # Look for a field that matches period pattern or has "最大" in it
        period_index = -1
        price_index = -1
        
        for j in range(3, len(parts)):
            if re.match(r'募集期間：.*|期間情報なし', parts[j]):
                period_index = j
                break
        
        if period_index == -1:
            # If no period field found, look for price field
            for j in range(3, len(parts)):
                if '万円' in parts[j] or '最大' in parts[j]:
                    price_index = j
                    break
        
        if period_index != -1:
            # We found the period field
            description = ','.join(parts[3:period_index])
            period = parts[period_index]
            price = parts[period_index + 1]
            section = parts[period_index + 2]
            selected_items = ','.join(parts[period_index + 3:])
            
            fixed_line = f'"{title}","{status}","{url}","{description}","{period}","{price}","{section}","{selected_items}"'
            fixed_lines.append(fixed_line)
        elif price_index != -1:
            # We found the price field
            description = ','.join(parts[3:price_index])
            price = parts[price_index]
            section = parts[price_index + 1]
            selected_items = ','.join(parts[price_index + 2:])
            
            fixed_line = f'"{title}","{status}","{url}","{description}","期間情報なし","{price}","{section}","{selected_items}"'
            fixed_lines.append(fixed_line)
        else:
            # Fallback - just use the original line
            fixed_lines.append(lines[i])
    
    # Write the fixed content to the output file
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        f.write('\n'.join(fixed_lines))
    
    print(f"Fixed CSV written to {output_file}")

# Example usage
fix_csv_format('subsidy_results.csv', 'fixed_subsidy_results.csv')