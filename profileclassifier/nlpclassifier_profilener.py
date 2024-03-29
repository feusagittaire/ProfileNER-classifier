import pandas as pd
import numpy as np
import re
from collections import defaultdict
import ast
from importlib import resources
import spacy
from spacy.util import minibatch, compounding
from spacy.pipeline import EntityRuler
from spacy.tokens import Span
from spacy.matcher import PhraseMatcher
from spacy.pipeline import EntityRuler

spacy.cli.download('pt_core_news_lg')

class NLPClassifier:

    def __init__(self, use, youtube: bool = False):
        uses = ['profile', 'ner']
        self.youtube = youtube
        ner_data = pd.read_csv(resources.open_binary('profileclassifier','ner_data.csv'), sep = ',')
        ner_data = ner_data.explode('names')
        if use in uses:
            self.use = use
        else:
            raise Exception('Function not included. Please select either profile or ner')

        #Lists containing the search string related to each profile category
        self.politico = pd.read_csv(resources.open_binary('profileclassifier','lista_politico.csv'), encoding='utf8')['politicos'].tolist()
        self.artista = ['singer',r'\bcantor',r'\batriz',r'\bator','comediante','youtuber', r'influenciado.* digital']
        midia_tradicional2 = pd.read_csv(resources.open_binary('profileclassifier','lista_midia_trad.csv'), encoding ='utf-8')['midias'].apply(lambda x:str(x).replace( ' ', '')).tolist()
        self.veiculo_info = pd.read_csv(resources.open_binary('profileclassifier','lista_midia_trad.csv'), encoding ='utf-8')['midias'].tolist() +midia_tradicional2
        self.saude = ['educacao fisica','physician ',r'\bnurse','emergency doc',r'medic.*',r'enfermeir.*',r'farmaceutic.*','fisioterapeuta',r'psicologo|psicologa','dentista',r'veterinari.*', 'nutricionista',r'fonoaudiolog.*','sanitarista','epidemiologista', r'(\bdr.\b).*especialista', r'(\bdr.\b).*treinamento fisico']
        self.jornalista = ['jornalista', 'reporter', 'cronista','ancora']
        universidades = pd.read_csv(resources.open_binary('profileclassifier','lista_unifederal.csv'), encoding ='utf-8', sep =',')['universidade'].tolist()
        self.org = pd.read_csv(resources.open_binary('profileclassifier','lista_org.csv'), encoding='utf8')['org'].tolist() + ['universidade federal','universidade estadual','universidade de sao paulo']
        self.prof_universidade = ["professor.*"+universidade for universidade in universidades]
        self.ciencia = [r'mestr. em',r'professor. universi.','research','scientific',r'\bmsc',r'\bphd', r'doutor.* em', 'doutorado em',r'div.*cientifica', r'divulgador.* cientific.*','cientista','pesquisador','pesquisadora',
        'grupo de pesquisa','rede de pesquisa','\bcnpq','comunicacao.*saude'] 

        parti = ['brasil247']
        midias_partidarias2 = pd.read_csv(resources.open_binary('profileclassifier','lista_midia_partidaria.csv'), encoding= 'utf-8')['midias'].apply(lambda x:str(x).replace( ' ', '')).tolist()
        self.midias_partidarias = pd.read_csv(resources.open_binary('profileclassifier','lista_midia_partidaria.csv'), encoding= 'utf-8')['midias'].tolist() + parti +midias_partidarias2
        self.educacao =  [r'professor.*ingles',r'professor.*portugues',r'professor.*espanhol', r'especialista.*ensino',r'professor.*libras',r'\bprof\b',r'educador.*',r'professor.*  filosofia',r'professor.*  fisica',r'professor.*  matematica',r'professor.*  quimica',r'professor.*  sociologia',
        r'professor.*  historia',r'professor.*  geografia', r'professor.*  biologia', r'professor.*  lingua',r'pedagog.','conteudo educativo']

        #NER
        self.ner_vac = ast.literal_eval(ner_data['names'].loc[0])
        self.ner_prod = ast.literal_eval(ner_data['names'].loc[1])
        self.ner_med = ast.literal_eval(ner_data['names'].loc[2])
        self.ner_freq = ast.literal_eval(ner_data['names'].loc[3])
        self.ner_doenca = ast.literal_eval(ner_data['names'].loc[4])
        self.ner_partes_corpo = ast.literal_eval(ner_data['names'].loc[5])
        self.ner_sci = ast.literal_eval(ner_data['names'].loc[6])
        self.ner_agente = ast.literal_eval(ner_data['names'].loc[7])
        self.ner_grave = ast.literal_eval(ner_data['names'].loc[8])
        self.ner_vac_pol = ast.literal_eval(ner_data['names'].loc[9])

        #As youtube has specific content directed to religious groups, those groups i.e channels are going to be classified.
        if youtube:
            self.religiao = ['igreja','pentecostal','crista','catolic.*','missionaria','islamismo','judaic.*',
            'judaismo','espirita','espiritismo','testemunha de jeova','umbanda','candomble','bispo']
        
        


    def att_profile_list(self,profile,new_words = []):
        ''' profile should be a string based on the profiles disponible in the package, 
        namely: politico, veiculo jornalistico, saude, jornalista, pesquisador, artista and org. 
        Besides, new_word should be a list.
        '''
        if profile == 'politico':
            for word in new_words:
                self.politico.append(word)
        if profile == 'veiculo_info':
            for word in new_words:
                self.veiculo_info.append(word)
        if profile == 'saude':
            for word in new_words:
                self.saude.append(word)
        if profile == 'jornalista':
            for word in new_words:
                self.jornalista.append(word)
        if profile == 'ciencia':
            for word in new_words:
                self.ciencia.append(word)
        if profile == 'artista':
            for word in new_words:
                self.artista.append(word)
        if profile == 'org':
            for word in new_words:
                self.org.append(word)
        if profile == 'educacao':
            for word in new_words:
                self.educacao.append(word)
        if profile == 'prof_universidade':
            for word in new_words:
                self.prof_universidade.append(word)


    def classifier(self, bio):
        '''Classify users/channels bases on their biographies/channel description. The profile categories 
        supported by this function are: political figure, journalistic vehicule, partisan media, governers, senators, 
        ministers, organizations,health communicators, journalists, education professionals, health professionals and artists. 
        If youtube, then there'll be also religious as category.

        '''
    
        if self.use == 'profile':
            for  text in self.politico: 
                if re.compile(text).search(bio):
                    return 'Político' 
            for text in self.artista:
                if re.compile(text).search(bio):
                    return 'Artista'
            for text in self.veiculo_info:
                if re.compile(text).search(bio):
                    return 'Veículo de informação'
            for text in self.org:
                if re.compile(text).search(bio):
                    return 'Organização'
            for text in self.saude:
                if re.compile(text).search(bio):
                    return "Prof. Saúde"
            for text in self.ciencia:
                if re.compile(text).search(bio):
                    return "Ciência"
            for text in self.jornalista:
                if re.compile(text).search(bio):
                    return "Jornalista"
            for text in self.educacao:
                if re.compile(text).search(bio):
                    return "Prof. Educação"
            for text in self.prof_universidade:
                if re.compile(text).search(bio):
                    return "Ciência"
            if self.youtube:
                for text in self.religiao:
                    if re.compile(text).search(bio):
                        return "Religião"

        elif self.use == 'ner':

            ner_dict = defaultdict(int)
                
            for text in self.ner_vac:
                if re.compile(text).search(bio):
                    ner_dict['vac'] += 1

            for text in self.ner_prod:
                if re.compile(text).search(bio):
                    ner_dict['prod'] += 1

            for text in self.ner_med:
                if re.compile(text).search(bio):
                    ner_dict['med'] += 1

            for text in self.ner_doenca:
                if re.compile(text).search(bio):
                    ner_dict['doenca'] += 1

            for text in self.ner_freq:
                if re.compile(text).search(bio):
                    ner_dict['freq'] += 1

            for text in self.ner_sci:
                if re.compile(text).search(bio):
                    ner_dict['sci'] += 1

            for text in self.ner_partes_corpo:
                if re.compile(text).search(bio):
                    ner_dict['partes_corpo'] += 1
            
            for text in self.ner_agente:
                if re.compile(text).search(bio):
                    ner_dict['agente'] += 1

            for text in self.ner_grave:
                if re.compile(text).search(bio):
                    ner_dict['eventos_graves'] += 1

            for text in self.ner_vac_pol:
                if re.compile(text).search(bio):
                    ner_dict['vac_pol'] += 1
            
            
            return ner_dict
            
    def nlp(self,model: str = 'pt_core_news_lg' ):
        nlp = spacy.load(model, disable = ['ner'])
        rulerAll = nlp.add_pipe('entity_ruler')
        for a in self.ner_vac:
            rulerAll.add_patterns([{"label": "VAC", "pattern": a}]) 
        
        for c in self.ner_prod:
            rulerAll.add_patterns([{"label": "PROD", "pattern": c}])
        for d in self.ner_med:
            rulerAll.add_patterns([{"label": "MED", "pattern": d}])
        for e in self.ner_freq:
            rulerAll.add_patterns([{"label": "EVENT_FREQ", "pattern": e}])
        for f in self.ner_grave:
            rulerAll.add_patterns([{"label": "EVENT_GRAVE", "pattern": f}])
        for g in self.ner_doenca:
            rulerAll.add_patterns([{"label": "DOENCA", "pattern": g}])
        for h in self.ner_partes_corpo:
            rulerAll.add_patterns([{"label": "PARTES_CORPO", "pattern": h}])
        for i in self.ner_sci:
            rulerAll.add_patterns([{"label": "SCI", "pattern": i}])
        for j in self.ner_agente:
            rulerAll.add_patterns([{"label": "AGENTE", "pattern": j}])
        for l in self.ner_vac_pol:
            rulerAll.add_patterns([{"label": "VAC_POLITCS", "pattern": l}])
        return nlp
    
    def ner_classifier(self,df,bio_column):
        ner_ = {'id':[],'ner':[],'total':[]}
        df = df.reset_index()
        ner_dict = df[bio_column].apply(lambda x: self.classifier(str(x)))
        for idx,x in enumerate(ner_dict):
            for k,e in x.items():
                ner_['id'].append(int(idx))
                ner_['ner'].append(k)
                ner_['total'].append(e)
        cols = pd.DataFrame(ner_['ner'], columns=['ner'])['ner'].unique()
        ner_df = pd.DataFrame()
        ner_df['id'] = ner_['id']
        ner_df = ner_df.drop_duplicates('id')
        ner_ref = pd.DataFrame.from_dict(ner_)
        for option in cols:
            ner_vac = ner_ref.loc[lambda x: x['ner'] == option]
            ner_vac[option] = ner_vac['total']
            ner_df = ner_df.merge(ner_vac[['id',option]], on = 'id', how = 'outer')
            ner_df = ner_df.fillna(0).astype(int)
        
        df['id'] = df.index
        df = df.merge(ner_df, on = 'id', how = 'outer')
        #df = df.fillna(0).astype(int)

        return df
    
        def show_ents(self, doc): 
            if doc.ents: 
                for ent in doc.ents: 
                    print(ent.text+' - ' +str(ent.start_char) +' - '+ str(ent.end_char) +' - '+ent.label_+ ' - '+str(spacy.explain(ent.label_))) 
            else: print('No named entities found.')

   

    def ner_en(self, x):
        ner = []
        for tok in x.ents:
            ner.append([tok.text,tok.label_])
        return ner
    
    def get_ner_en(self, df):
        token = {'tokens':[],'ner':[]}
        for x in df['ner']:
            for a,b in x:
                token['tokens'].append(a)
                token['ner'].append(b)
        ner = pd.DataFrame(token)
        return ner

