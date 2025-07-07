import yaml
import os
from typing import Dict, Any
from scraper_simplified import extract_complete_data

def load_config() -> Dict[str, Any]:
    """
    Loads configuration values from the config.yml file
    
    Returns:
        dict: Dictionary with configuration values
    """
    config_path = os.path.join(os.path.dirname(__file__), 'config.yml')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file: {e}")

def get_config_variables():
    """
    Gets values from config.yml and stores them in variables
    
    Returns:
        tuple: (regione, provincia, comune)
    """
    config = load_config()
    
    # Extract configuration values
    regione = config.get('regione', '')
    provincia = config.get('provincia', '')
    comune = config.get('comune', '')
    
    # Optional: print loaded values
    print(f"Configuration loaded:")
    print(f"  Regione: {regione}")
    print(f"  Provincia: {provincia}")
    print(f"  Comune: {comune}")
    
    return regione, provincia, comune

# Usage example
if __name__ == "__main__":
    # Load configuration variables
    regione, provincia, comune = get_config_variables()
    
    # Set output directory
    output_directory = "extracted_data"
    
    # Extract data using the simplified scraper
    print(f"\nStarting data extraction...")
    total_records, data = extract_complete_data(regione, provincia, comune, output_directory)
    
    print(f"\n🎯 EXTRACTION SUMMARY:")
    print(f"   📋 Region: {regione}")
    print(f"   🏛️ Province: {provincia}")  
    print(f"   🏘️ Commune: {comune}")
    print(f"   ✅ Total records extracted: {total_records}")
    print(f"   📁 Data saved in: {output_directory}")
    
    if total_records > 0:
        print(f"\n✅ Extraction completed successfully!")
    else:
        print(f"\n⚠️ No records were extracted. Check the filters and try again.")