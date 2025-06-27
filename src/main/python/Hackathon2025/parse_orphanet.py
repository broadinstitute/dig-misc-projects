
import xml.etree.ElementTree as ET
import csv

# constants
DIR_DATA = '/Users/mduby/Data/Broad/Hackathon25/Data'
FILE_ORPHA_XML = "{}/ORPHAlinearisation_en_2024.xml".format(DIR_DATA)
FILE_ORPHA_OUT = "{}/orpha_parsed.tsv".format(DIR_DATA)

def parse_orpha_xml(input_file, output_file):
    """
    Parse XML file to extract OrphaCode to Name mapping and save to TSV.
    
    Args:
        input_file (str): Path to input XML file
        output_file (str): Path to output TSV file
    """
    
    # Parse the XML file
    tree = ET.parse(input_file)
    root = tree.getroot()
    
    # Dictionary to store orpha code to name mapping
    orpha_map = {}
    
    # Find all Disorder elements
    for disorder in root.findall('.//Disorder'):
        # Extract OrphaCode
        orpha_code_elem = disorder.find('OrphaCode')
        # Extract Name (with lang="en")
        name_elem = disorder.find('Name[@lang="en"]')
        
        if orpha_code_elem is not None and name_elem is not None:
            orpha_code = orpha_code_elem.text
            name = name_elem.text
            orpha_map[orpha_code] = name
    
    # Write to TSV file
    with open(output_file, 'w', newline='', encoding='utf-8') as tsvfile:
        writer = csv.writer(tsvfile, delimiter='\t')
        
        # Write header
        writer.writerow(['OrphaCode', 'Name'])
        
        # Write data (sorted by OrphaCode for consistency)
        for orpha_code in sorted(orpha_map.keys(), key=int):
            writer.writerow([orpha_code, orpha_map[orpha_code]])
    
    print(f"Extracted {len(orpha_map)} Orpha codes to {output_file}")
    return orpha_map

# Example usage
if __name__ == "__main__":
    # Replace with your actual file paths
    # input_xml_file = "orpha_disorders.xml"
    # output_tsv_file = "orpha_codes.tsv"
    input_xml_file = FILE_ORPHA_XML
    output_tsv_file = FILE_ORPHA_OUT
    
    try:
        orpha_mapping = parse_orpha_xml(input_xml_file, output_tsv_file)
        
        # Print first few entries as verification
        print("\nFirst 5 entries:")
        for i, (code, name) in enumerate(sorted(orpha_mapping.items(), key=lambda x: int(x[0]))):
            if i < 5:
                print(f"{code}\t{name}")
            else:
                break
                
    except FileNotFoundError:
        print(f"Error: Could not find input file '{input_xml_file}'")
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
    except Exception as e:
        print(f"Error: {e}")



