#!/usr/bin/env python3
"""
Standalone Polar Generation Engine for Production Deployment
Based on the working polar generator that successfully created Aurelius polar
"""

import csv
import json
import os
import tempfile
from datetime import datetime
from collections import defaultdict
import statistics

def parse_expedition_file(file_path):
    """Parse Expedition CSV file format"""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Find data start (skip header lines)
        data_start = 0
        for i, line in enumerate(lines):
            if line.startswith('0,') and ',' in line and len(line.split(',')) > 10:
                data_start = i
                break
        
        if data_start == 0:
            return []
            
        # Parse data lines into structured format
        data_rows = []
        for line in lines[data_start:]:
            if line.strip() and not line.startswith('!'):
                parts = line.strip().split(',')
                if len(parts) >= 10:
                    try:
                        # Parse index,value pairs
                        data_dict = {}
                        for i in range(0, len(parts)-1, 2):
                            if i+1 < len(parts):
                                try:
                                    index = int(parts[i])
                                    value = float(parts[i+1])
                                    data_dict[index] = value
                                except (ValueError, IndexError):
                                    continue
                        
                        if data_dict:
                            data_rows.append(data_dict)
                    except Exception:
                        continue
        
        return data_rows
    except Exception as e:
        print(f"Error parsing file {file_path}: {e}")
        return []

def extract_sailing_data(data_rows):
    """Extract sailing data from parsed rows"""
    sailing_data = []
    
    for row in data_rows:
        try:
            # Extract key sailing parameters
            # Common Expedition indices: TWS=2, TWA=3, BSP=1, SOG=4, etc.
            tws = row.get(2)  # True Wind Speed
            twa = row.get(3)  # True Wind Angle  
            bsp = row.get(1)  # Boat Speed
            sog = row.get(4)  # Speed Over Ground
            
            # Use SOG if BSP not available
            boat_speed = bsp if bsp and bsp > 0 else sog
            
            if tws and twa is not None and boat_speed and tws > 0 and boat_speed > 0:
                sailing_data.append({
                    'TWS': tws,
                    'TWA': abs(twa),  # Use absolute value
                    'BSP': boat_speed
                })
        except Exception:
            continue
    
    return sailing_data

def clean_sailing_data(sailing_data):
    """Clean and filter sailing data"""
    clean_data = []
    
    for point in sailing_data:
        tws = point['TWS']
        twa = point['TWA']
        bsp = point['BSP']
        
        # Filter reasonable sailing conditions
        if (2 <= tws <= 30 and  # Wind speed range
            5 <= twa <= 180 and  # Wind angle range
            1 <= bsp <= 25):     # Boat speed range
            clean_data.append(point)
    
    return clean_data

def generate_polar_data(sailing_data):
    """Generate polar data from sailing data"""
    # Wind speed bins
    wind_bins = [6, 8, 10, 12, 14, 16, 20, 24]
    
    # Angle bins (every 15 degrees)
    angle_bins = list(range(0, 181, 15))
    
    polar_data = {}
    data_quality = {}
    
    for wind_speed in wind_bins:
        # Filter data for this wind speed bin (±1 knot)
        wind_data = [d for d in sailing_data 
                    if wind_speed - 1 <= d['TWS'] <= wind_speed + 1]
        
        if not wind_data:
            continue
            
        angles_speeds = []
        bin_quality = {}
        
        for angle in angle_bins:
            # Filter data for this angle bin (±7.5 degrees)
            angle_data = [d for d in wind_data 
                         if angle - 7.5 <= d['TWA'] <= angle + 7.5]
            
            if len(angle_data) >= 2:  # Minimum data points
                speeds = [d['BSP'] for d in angle_data]
                
                # Use 85th percentile for target speed
                target_speed = statistics.quantiles(speeds, n=20)[16]  # 85th percentile
                
                angles_speeds.extend([angle, round(target_speed, 2)])
                bin_quality[angle] = len(angle_data)
        
        if angles_speeds:
            polar_data[wind_speed] = angles_speeds
            data_quality[wind_speed] = bin_quality
    
    return polar_data, data_quality

def format_expedition_polar(polar_data, boat_name):
    """Format polar data in Expedition format"""
    lines = [f"!{boat_name}%"]
    
    wind_speeds = sorted(polar_data.keys())
    for wind_speed in wind_speeds:
        angles_speeds = polar_data[wind_speed]
        line = f"{wind_speed}"
        for value in angles_speeds:
            line += f" {value}"
        lines.append(line)
    
    return "\n".join(lines)

def process_log_files(file_paths, boat_name="Boat"):
    """Process multiple log files and generate polar"""
    all_sailing_data = []
    
    for file_path in file_paths:
        print(f"Processing {file_path}...")
        data_rows = parse_expedition_file(file_path)
        sailing_data = extract_sailing_data(data_rows)
        clean_data = clean_sailing_data(sailing_data)
        all_sailing_data.extend(clean_data)
        print(f"  Extracted {len(clean_data)} clean data points")
    
    print(f"\nTotal clean data points: {len(all_sailing_data)}")
    
    if len(all_sailing_data) < 100:
        return None, "Insufficient data for polar generation (minimum 100 points required)"
    
    # Generate polar
    polar_data, data_quality = generate_polar_data(all_sailing_data)
    
    if not polar_data:
        return None, "No valid polar data generated"
    
    # Format as Expedition polar
    expedition_polar = format_expedition_polar(polar_data, boat_name)
    
    # Create summary
    summary = {
        'total_points': len(all_sailing_data),
        'wind_bins': len(polar_data),
        'data_quality': data_quality,
        'wind_range': f"{min(polar_data.keys())}-{max(polar_data.keys())} knots"
    }
    
    return expedition_polar, summary

if __name__ == "__main__":
    # Test the engine
    test_files = ["/home/ubuntu/upload/log-2025Mar14.csv"]
    polar, summary = process_log_files(test_files, "TestBoat")
    if polar:
        print("Polar generated successfully!")
        print(f"Summary: {summary}")
    else:
        print(f"Error: {summary}")

