from six.moves import urllib
import os
import pandas as pd
import re

def files_downloader(file):
    if (str(file)+'.xlsx') not in os.listdir("downloaded_files\\"):
        url = 'https://www.vendeeglobe.org/download-race-data/vendeeglobe_'+file+'.xlsx'
        urllib.request.urlretrieve(url,"downloaded_files\\"+file+'.xlsx')

def converter(dms_coor,rang):
    dd_coord=[]
    for val,rank in zip(dms_coor,rang):
        if (rank == 'RET') or (rank == 'NL'):
            dd_coord.append('NaN')
        else:
            deg, minutes, direction =  re.split('[°\']', val)
            dd_coord.append((float(deg) + float(minutes)/60) * (-1 if direction in ['W', 'S'] else 1))
    return dd_coord

def merger(file):

    df = pd.DataFrame()

    if "caracteristiques" not in file:
        path_excel = "downloaded_files\\"+file
        print(path_excel)
        df = pd.read_excel(path_excel, encoding='utf-8',usecols = [i for i in range(1,21)], names=['rang','num','nom','heure','lat','lon','cap30','vit30','vmg30','dist30','capLast','vitLast','vmgLast','distLast','cap24','vit24','vmg24','dist24','dtf','dtl'])
        jour = df.rang.loc[1].split()[3]
        mois = df.rang.loc[1].split()[4]
        df = df.loc[4:36]
        df = df.reset_index(drop=True)
        df['lat'] = converter(df['lat'].values.tolist(),df['rang'].values.tolist())
        df['lon'] = converter(df['lon'].values.tolist(),df['rang'].values.tolist())
        df['nat'] = df['num'].apply(lambda x : str(x).split('\n')[1].split()[0])
        df['num'] = df['num'].apply(lambda x : str(x).split('\n')[1].split()[1])
        df['nom'] = df['nom'].apply(lambda x : str(x).split('\n')[0])
        df['heure'] = df['heure'].apply(lambda x : str(x).split('\n')[0].split(' ')[0])
        df.insert(loc=4, column='jour', value=jour)
        df.insert(loc=5, column='mois', value=mois)
        df['cap30'] = df['cap30'].apply(lambda x : str(x).split('°')[0])
        df['vit30'] = df['vit30'].apply(lambda x : str(x).split('kts')[0])
        df['vmg30'] = df['vmg30'].apply(lambda x : str(x).split('kts')[0])
        df['dist30'] = df['dist30'].apply(lambda x : str(x).split('nm')[0])
        df['capLast'] = df['capLast'].apply(lambda x : str(x).split('°')[0])
        df['vitLast'] = df['vitLast'].apply(lambda x : str(x).split('kts')[0])
        df['vmgLast'] = df['vmgLast'].apply(lambda x : str(x).split('kts')[0])
        df['distLast'] = df['distLast'].apply(lambda x : str(x).split('nm')[0])
        df['cap24'] = df['cap24'].apply(lambda x : str(x).split('°')[0])
        df['vit24'] = df['vit24'].apply(lambda x : str(x).split('kts')[0])
        df['vmg24'] = df['vmg24'].apply(lambda x : str(x).split('kts')[0])
        df['dist24'] = df['dist24'].apply(lambda x : str(x).split('nm')[0])
        df['dtf'] = df['dtf'].apply(lambda x : str(x).split(' ')[0])
        df['dtl'] = df['dtl'].apply(lambda x : str(x).split(' ')[0])
        
        indexNames = df[(df['rang'] == 'NL') | (df['rang'] == 'RET')].index
        # Delete these row indexes from dataFrame
        df.drop(indexNames , inplace=True)
        df = df.reset_index(drop=True)
        df[["vit30","vmg30","dist30","vitLast","vmgLast","distLast","vit24","vmg24","dist24","dtf","dtl"]] = df[["vit30","vmg30","dist30","vitLast","vmgLast","distLast","vit24","vmg24","dist24","dtf","dtl"]].apply(pd.to_numeric)
        
    return df

def caracteristiques_downloader():
    dico = {}
    glossaire = open('glossaire_bateaux.html',encoding='utf-8')
    glossaire = iter(glossaire)
    for line in glossaire:
        if '<span class="boats-list__skipper-name">' in line:
            temp = line
            name = temp.split('>')[1].split('</span')[0]
            dico.setdefault(name,[])

            subGlossaire = []
            while (len(subGlossaire)<23):
                subGlossaire.append(next(glossaire))

            count = 0
            temp_list=[]
            for line in subGlossaire: 
                temp = line
                if 'lancement' in temp:
                    dico[name].append(temp.split('</li>')[0].split(" ")[-1])
                if 'Longueur' in temp:
                    lon = temp.split('<li>')[1].split('</li>')[0].split(' : ')[1].split()[0]
                    if 'm' in lon:
                        dico[name].append(lon.split('m')[0])
                    else:
                        dico[name].append(lon)
                if 'Largeur' in temp:
                    lar = temp.split('<li>')[1].split('</li>')[0].split(' : ')[1].split()[0]
                    if 'm' in lar:
                        dico[name].append(lar.split('m')[0])
                    else:
                        dico[name].append(lar)
                if 'Tirant' in temp:
                    tir = temp.split('<li>')[1].split('</li>')[0].split(' : ')[1].split()[0]
                    if 'm' in tir:
                        dico[name].append(tir.split('m')[0])
                    else:
                        dico[name].append(tir)
                if 'Déplacement' in temp:
                    dep = temp.split('<li>')[1].split('</li>')[0].split(' : ')[1].split('t')[0]
                    if 'nc' in dep.lower():
                        dico[name].append('NaN')
                    elif ' ' in dep:
                        dico[name].append(dep.split()[0])
                    else:
                        dico[name].append(dep)
                if 'dérives' in temp:
                    dico[name].append(temp.split('<li>')[1].split('</li>')[0].split(' : ')[1])
                if 'Voile quille' in temp:
                    temp_list.append(temp.split('<li>')[1].split('</li>')[0].split(' : ')[1])
                    count+=1
                if 'voiles au près' in temp:
                    dico[name].append(temp.split('<li>')[1].split('</li>')[0].split(' : ')[1].split()[0])
                if 'voiles au portant' in temp:
                    dico[name].append(temp.split('<li>')[1].split('</li>')[0].split(' : ')[1].split()[0])

            if count == 0:
                dico[name].append('NaN')
            else:
                dico[name].append(temp_list[0])
            continue
    
    caract = pd.DataFrame.from_dict(dico, orient ='index',columns=['lancement','longueur','largeur','tirant','deplacement','derive','voilePres','voilePortant','voileQuille'])
    
    caract.to_excel("downloaded_files\\caracteristiques.xlsx")