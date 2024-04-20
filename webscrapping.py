import sys
import requests
from bs4 import BeautifulSoup
import re
import unicodedata
import pandas as pd


def extract_column_from_header(table):
    """
    This function returns the landing status from the HTML table cell 
    Input: the  element of a table data cell extracts extra row
    """
    wrong_columns = ['\n','1\n','2\n','3\n','4\n','5\n','6\n','7\n']
    columns = []
    for i,row in enumerate(table):
        if (row.br):
            row.br.extract()
        if row.a:
            row.a.extract()
        if row.sup:
            row.sup.extract()
            
        colunm_name = ' '.join(row.contents)
    
        # Filter the digit and empty names
        if not(colunm_name.strip().isdigit()):
            colunm_name = colunm_name.strip()
        
        if colunm_name != None and colunm_name != '' and colunm_name not in wrong_columns:
            columns.append(colunm_name)

    return columns

def create_df(col_names, soap):
    launch_dict = create_dict_(col_names)

    extracted_row = 0
    #Extract each table 
    for table_number,table in enumerate(soap.find_all('table',"wikitable plainrowheaders collapsible")):
    # get table row 
        for rows in table.find_all("tr"):
            #check to see if first table heading is as number corresponding to launch a number 
            if rows.th:
                if rows.th.string:
                    flight_number=rows.th.string.strip()
                    flag=flight_number.isdigit()
            else:
                flag=False
            #get table element 
            row=rows.find_all('td')
            #if it is number save cells in a dictonary 
            if flag:
                extracted_row += 1
                # Flight Number value
                # TODO: Append the flight_number into launch_dict with key `Flight No.`                
                launch_dict['Flight No.'].append(flight_number) 

                # Date value
                # TODO: Append the date into launch_dict with key `Date`
                datatimelist=date_time(row[0])
                date = datatimelist[0].strip(',')
                launch_dict['Date'].append(date)
                #print(date)
                
                # Time value
                # TODO: Append the time into launch_dict with key `Time`
                time = datatimelist[1]
                launch_dict["Time"].append(time)
                #print(time)
                
                # Booster version
                # TODO: Append the bv into launch_dict with key `Version Booster`
                bv=booster_version(row[1])
                if not(bv):
                    bv=row[1].a.string
                launch_dict['Version Booster'].append(bv)
                #print(bv)
                
                # Launch Site
                # TODO: Append the bv into launch_dict with key `Launch Site`
                launch_site = row[2].a.string
                launch_dict['Launch site'].append(launch_site)
                #print(launch_site)
                
                # Payload
                # TODO: Append the payload into launch_dict with key `Payload`
                payload = row[3].a.string
                launch_dict['Payload'].append(payload)
                #print(payload)
                
                # Payload Mass
                # TODO: Append the payload_mass into launch_dict with key `Payload mass`
                payload_mass = get_mass(row[4])
                launch_dict['Payload mass'].append(payload_mass)
                #print(payload)
                
                # Orbit
                orbit = row[5].a.string
                launch_dict['Orbit'].append(orbit)
                #print(orbit)
                
                # Customer
                #if type(row[6]) == 'bs4.element.Tag':
                if row[6].a:
                    customer = row[6].a.string
                    launch_dict['Customer'].append(customer)

                # Launch outcome
                launch_outcome = list(row[7].strings)[0]
                launch_dict['Launch outcome'].append(launch_outcome)
                
                # Booster landing
                booster_landing = landing_status(row[8])
                launch_dict['Booster landing'].append(booster_landing)
    return launch_dict

def create_dict_(column_names):
    launch_dict= dict.fromkeys(column_names)

    # Remove an irrelvant column
    del launch_dict['Date and time ( )']
    # Let's initial the launch_dict with each value to be an empty list
    launch_dict['Flight No.'] = []
    launch_dict['Launch site'] = []
    launch_dict['Payload'] = []
    launch_dict['Payload mass'] = []
    launch_dict['Orbit'] = []
    launch_dict['Customer'] = []
    launch_dict['Launch outcome'] = []
    # Added some new columns
    launch_dict['Version Booster']=[]
    launch_dict['Booster landing']=[]
    launch_dict['Date']=[]
    launch_dict['Time']=[]
    return launch_dict

def date_time(table_cells):
    """
    This function returns the data and time from the HTML  table cell
    Input: the  element of a table data cell extracts extra row
    """
    return [data_time.strip() for data_time in list(table_cells.strings)][0:2]

def booster_version(table_cells):
    """
    This function returns the booster version from the HTML  table cell 
    Input: the  element of a table data cell extracts extra row
    """
    out=''.join([booster_version for i,booster_version in enumerate( table_cells.strings) if i%2==0][0:-1])
    return out

def landing_status(table_cells):
    """
    This function returns the landing status from the HTML table cell 
    Input: the  element of a table data cell extracts extra row
    """
    out=[i for i in table_cells.strings][0]
    return out


def get_mass(table_cells):
    mass=unicodedata.normalize("NFKD", table_cells.text).strip()
    if mass:
        mass.find("kg")
        new_mass=mass[0:mass.find("kg")+2]
    else:
        new_mass=0
    return new_mass

def main():
    static_url = "https://en.wikipedia.org/w/index.php?title=List_of_Falcon_9_and_Falcon_Heavy_launches&oldid=1027686922"

    res = requests.get(static_url).text    # assign the response to a object
    soap = BeautifulSoup(res, "html.parser")  # Use BeautifulSoup() to create a BeautifulSoup
    html_tables = soap.find_all('table')

    first_lnch_table = html_tables[2].find_all('th')
    
    # Obtain table columns
    column_names = extract_column_from_header(first_lnch_table)

    # Store data returned into dataframe 
    lunch_dict = create_df(column_names, soap)

    # Create datafrmae that 
    df= pd.DataFrame({ key:pd.Series(value) for key, value in lunch_dict.items() })
    df.head()

    # Export data into CSV file 
    df.to_csv('webscrapping_data.csv', index=False)
if __name__ == '__main__':
  main()


