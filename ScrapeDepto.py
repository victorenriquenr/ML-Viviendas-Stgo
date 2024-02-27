#!----------------------------------------------------------------------------------
#!----------------------------------------------------------------------------------
#!Proyecto: Extracción de datos de venta de departamentos en Santigao de Chile
#! Fuente: https:www.chilepropiedades.cl
#!
#!@autor: Víctor E. Núñez
#!Ultima actualización: 25 de Febrero de 2024
#!----------------------------------------------------------------------------------
#!----------------------------------------------------------------------------------

from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from lxml import html
import re
import time
import numpy as np, pandas as pd

#---------------------------------------------------------------------------------
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/181.0.0.0 Safari/537.36",
}

class Content:
    def __init__(self,Address, Price_CLP, Price_UF, HOA_fees, Bedrooms, 
                 Bathrooms, Floor, Garage, Total_area, Usable_area,Interior, 
                 Exterior, Services, Flooring_type, Description, Nearby_amenities, Type, 
                 Category, Publication_date, Real_estate_agent, Publication_ID, Link):
        self.Address =  Address
        self.Link = Link
        self.Price_CLP = Price_CLP
        self.Price_UF = Price_UF
        self.HOA_fees =  HOA_fees
        self.Bedrooms = Bedrooms
        self.Bathrooms =  Bathrooms
        self.Floor =  Floor
        self.Garage = Garage
        self.Total_area = Total_area
        self.Usable_area =  Usable_area
        self.Interior =  Interior
        self.Exterior = Exterior
        self.Services =  Services
        self.Flooring_type =  Flooring_type
        self.Description =  Description
        self.Nearby_amenities =  Nearby_amenities
        self.Type =  Type
        self.Category =  Category
        self.Publication_date =  Publication_date
        self.Real_estate_agent =  Real_estate_agent
        self.Publication_ID =  Publication_ID
    
    
    def to_dataframe(self):
        data = {
            'Address': self.Address,
            'Price_CLP': self.Price_CLP,
            'Price_UF': self.Price_UF,
            'HOA_fees': self.HOA_fees,
            'Bedrooms': self.Bedrooms,
            'Bathrooms': self.Bathrooms,
            'Floor': self.Floor,
            'Garage': self.Garage,
            'Total_area': self.Total_area,
            'Usable_area': self.Usable_area,
            'Interior': self.Interior,
            'Exterior': self.Exterior,
            'Services': self.Services,
            'Flooring_type': self.Flooring_type,
            'Description': self.Description,
            'Nearby_amenities': self.Nearby_amenities,
            'Type': self.Type,
            'Category': self.Category,
            'Publication_date': self.Publication_date,
            'Real_estate_agent': self.Real_estate_agent,
            'Publication_ID': self.Publication_ID,
            'Link': self.Link
        }
        df = pd.DataFrame(data)
        return df


def getSoup(url):
    req = requests.get(url, headers = headers)
    soup = BeautifulSoup(req.text, 'html.parser')
    parser = html.fromstring(req.content)
    return soup, parser

def InternalLinks(url):
    internalLinks = []
    soup, parser = getSoup(url)
    links =  soup.find_all('a', href = re.compile(r'/ver-publicacion/venta/.*', re.IGNORECASE))
    for link in links:
        link = 'https://chilepropiedades.cl'+link.get('href')
        if link not in internalLinks:
            internalLinks.append(link)  
    return internalLinks


def ScrapePage(url,numPage,delay):
   
    #Ajustamos el limite de paginas que podemos extraer.
    soup, parser =  getSoup(url)
    total_pages = int(soup.find_all('a', class_= "page-link")[-1].get('href').split('/')[-1])
    
    if numPage > total_pages:
        numPage = total_pages

    print('Extrayendo datos de {} páginas para departamentos en venta en {}:'.format(numPage, url.split('/')[-2]) )
    print(' ')
    
    Address = []; Link = [];
    Price_CLP = []; Price_UF = [];
    HOA_fees = []; Bedrooms = [];
    Bathrooms = []; Floor = [];
    Garage = [];
    Total_area = []; Usable_area = [];
    Type = []; Category = [];
    Publication_date = []; Publication_ID = [];
    Interior = []; Exterior=[];
    Flooring_type = []; Services = [];
    Description = []; Nearby_amenities = [];
    Real_estate_agent = [];
    url_ = url
    while numPage != 0:
        #print('Extrayendo datos de: ', url_)
        links =  InternalLinks(url_)
        for element in links:
            soup,parser = getSoup(element)

            #Link------------------------------------------------------
            Link.append(element)
            #Address-------------------------------------------------
            try:
                Address.append(soup.find('h1').get_text().replace('\n', '').strip())
            except:
                Address.append(np.nan)

            #-----------------------------------------------------------
            # Primera Tabla
            #-----------------------------------------------------------
            
            dict={}
            for key,value in zip(soup.find_all('div', class_ = "clp-description-label col-6"),
                                 soup.find_all('div', class_ = "clp-description-value col-6")
                                ):
                key =  key.get_text().strip()
                value =  value.get_text().replace('  ','').strip()
                dict[key] =  value

            #-----------------------------------------------------------
           #Valor
            try:
                if dict['Valor (CLP aprox.)*:']:
                    Valor_CLP_ = dict['Valor (CLP aprox.)*:'].split()[1]
                    Price_CLP.append(Valor_CLP_)
                    Valor_UF_  = dict['Valor:'].split()[1]
                    Price_UF.append(Valor_UF_)
            except:
                Valor_CLP_  = dict['Valor:'].split()[1]
                Price_CLP.append(Valor_CLP_)
                Valor_UF_ = dict['Valor (UF aprox.)*:'].split()[1]
                Price_UF.append(Valor_UF_)

             
            #Gastos Comunes--------------------------------------------
            try:
                HOA_fees.append(dict['Gastos Comunes:'].split()[1])
            except:
                HOA_fees.append(np.nan)
            #Rooms----------------------------------------------
            try:
                Bedrooms.append(int(dict['Habitaciones:']))
            except:
                Bedrooms.append(np.nan)
            #Bathrooms-----------------------------------------------------
            try:
                Bathrooms.append(int(dict['Baño:']))
            except:
                Bathrooms.append(np.nan)
            #Floor------------------------------------------------------
            try:
                Floor.append(int(dict['Piso:']))
            except:
                Floor.append(np.nan)
            #Garage------------------------------------------
            try:
                Garage.append(int(dict['Estacionamientos:']))
            except:
                Garage.append('No')
            #Superficie Total------------------------------------------
            try:
                Total_area.append(dict['Superficie Total:'])
            except:
                Total_area.append(np.nan)
            #Superficie Util-------------------------------------------
            try:
                Usable_area.append(dict['Superficie Útil:'])
            except:
                Usable_area.append(np.nan)

            #----------------------------------------------------------
            # Segunda Tabla
            #----------------------------------------------------------
            
            dict_2 = {}

            for key,value in zip(soup.find_all('div', class_ = "col-6 clp-description-label"),
                                 soup.find_all('div', class_ = "col-6 clp-description-value")
                                ):
                key =  key.get_text().strip()
                value =  value.get_text().replace('  ','').strip()
                dict_2[key] =  value
            #----------------------------------------------------------
            #Category
            try:
                Type.append(dict_2['Tipo de publicación:'])
            except:
                Type.append(np.nan)
            #Category de Propiedad----------------------------------------
            try:
                Category.append(dict_2['Tipo de propiedad:'])
            except:
                Category.append(np.nan)
            #Fecha de Publicación--------------------------------------
            try:
                Publication_date.append(dict_2['Fecha Publicación:'])
            except:
                Publication_date.append(np.nan)
            #Publication_ID----------------------------------------------------
            try:
                Publication_ID.append(dict_2['Código aviso:'])
            except:
                Publication_ID.append(np.nan)
            #----------------------------------------------------------
            # Services
            #----------------------------------------------------------
            servicios = {}
            if soup.find('ul', class_="clp-equipment-list"):
                for element in soup.find('ul', class_="clp-equipment-list").get_text().strip().split('\n')[:4]:
                    try:
                        key = element.split(':')[0]
                        value = element.split(':')[1]
                        servicios[key] = value
                    except:
                        None
                        
            else:
                servicios['Interior'] = np.nan
                servicios['Exterior'] = np.nan
                servicios['Servicios'] = np.nan
                servicios['Piso'] = np.nan
            
            #Interior--------------------------------------------------------
            try:
                Interior.append(servicios['Interior'])
            except:
                Interior.append(np.nan)
            #Exterior--------------------------------------------------------
            try:
                Exterior.append(servicios['Exterior'])
            except:
                Exterior.append(np.nan)
            #Services-------------------------------------------------------
            try:
                Services.append(servicios['Servicios'])
            except:
                Services.append(np.nan)
            #Tiṕo de Floor----------------------------------------------------
            try:
                Flooring_type.append(servicios['Piso'])
            except:
                Flooring_type.append(np.nan)
            
            #Description-----------------------------------------------------
            text =[]
            if soup.find('div', class_="clp-description-box"):
                try: 
                    for element in soup.find('div', class_="clp-description-box"):
                        text.append(element.get_text().strip())
                    Description.append(" ".join(text))
                except:
                    Description.append(np.nan)
            else: 
                Description.append(np.nan)
            #Lugares Nearby_amenitiess de interes--------------------------------------
            if soup.find_all('h2', string = 'Comodidades y Lugares de Interés'):
                try: 
                    list_ = []
                    for div in soup.find_all('div', class_= 'amenity-text'):
                        Nearby_amenities_ = div.find('p').get_text().replace('', '').split('\n')
                        Nearby_amenities_ = list(filter(lambda x: x.strip(), Nearby_amenities_))
                        list_.append(Nearby_amenities_[0].strip()+' ('+Nearby_amenities_[-1].strip()+')')
                    Nearby_amenities.append(list_)
                except:
                    Nearby_amenities.append(np.nan)
            else:
                Nearby_amenities.append(np.nan)
            #Real_estate_agent-------------------------------------------------------
            if soup.find_all('h2', string='Corredora'):
                try:
                    Real_estate_agent_ = soup.find('div', class_= "col-sm-8 clp-user-contact-details-table").find('a').get_text()
                    Real_estate_agent.append(Real_estate_agent_)
                except:
                    Real_estate_agent.append(np.nan)
            else:
                Real_estate_agent.append(np.nan)    
            
        
        time.sleep(delay)
        numPage = numPage-1
        if numPage == 0:
            break
        next_soup, next_ṕarser = getSoup(url_)
        url_ = next_soup.find('link', {'rel':'next'}).get('href')
        
    return Content(Address,Price_CLP,Price_UF,HOA_fees, Bedrooms,
                   Bathrooms, Floor, Garage, Total_area, Usable_area, Interior,
                   Exterior, Services, Flooring_type, Description, Nearby_amenities, Type, Category, 
                   Publication_date,Real_estate_agent, Publication_ID ,Link)


# Crear los DataFrames vacíos
dataframe1 = pd.DataFrame()
dataframe2 = pd.DataFrame()
dataframe3 = pd.DataFrame()
dataframe4 = pd.DataFrame()
dataframe5 = pd.DataFrame()
dataframe6 = pd.DataFrame()
dataframe7 = pd.DataFrame()
dataframe8 = pd.DataFrame()

for element in ['santiago','las-condes', 'nunoa', 'providencia', 'estacion-central',
               'san-miguel', 'vitacura', 'independencia']:
    start_url = 'https://chilepropiedades.cl/propiedades/venta/departamento/{}/0'.format(element)
    
    content = ScrapePage(start_url,1,2) 
    
    new_df = content.to_dataframe()  # Llama al método to_dataframe() del objeto Content
    
    # Determinar cuál es el DataFrame correspondiente y concatenar el nuevo DataFrame
    if element == 'santiago':
        dataframe1 = pd.concat([dataframe1, new_df],axis = 0, ignore_index=True)
    elif element == 'las-condes':
        dataframe2 = pd.concat([dataframe2, new_df], ignore_index=True)
    elif element == 'nunoa':
        dataframe3 = pd.concat([dataframe3, new_df], ignore_index=True)
    elif element == 'providencia':
        dataframe4 = pd.concat([dataframe4, new_df], ignore_index=True)
    elif element == 'estacion-central':
        dataframe5 = pd.concat([dataframe5, new_df], ignore_index=True)
    elif element == 'san-miguel':
        dataframe6 = pd.concat([dataframe6, new_df], ignore_index=True)
    elif element == 'vitacura':
        dataframe7 = pd.concat([dataframe7, new_df], ignore_index=True)
    elif element == 'independencia':
        dataframe8 = pd.concat([dataframe8, new_df], ignore_index=True)
    

final_df = pd.concat([dataframe1, dataframe2, dataframe3, dataframe4,
                     dataframe5, dataframe6, dataframe7, dataframe8], axis = 0).reset_index(drop =  True)
#Guardamos el dataset:
#final_df.to_csv('./Dataset_DeptoStgoCHL.csv')

print('¡Extracción Completada!')