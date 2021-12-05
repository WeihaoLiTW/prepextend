# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 22:04:35 2020

@author: weiha
"""

from zipfile import ZipFile
import json
import logging as log

# flow_file = path\to\flow_file

class decode_flow:
    
    def __init__(self, flow_file = 'None'
                 ):    
        
        self.path = flow_file
        
        self.conn_class_info_dict = {'hyper':'dbname',
                                     'excel-direct':'filename'
                                    }
        self.output_types = ['csvOutputFile', 'hyperOutputFile']      
        self.input_name = 'input'
        self.output_name = 'output'
        
        if self.path != 'None':
            self.flow = self.get_flow()
        
        self.source_format = {
            'baseType':'',
            'con_type':'',
            'name':'',
            'server':'',
            'dbname':'',
            'table':'',
            'project':'',
            'datasourceName':''
            }
    
    def get_flow(self):
        # ref: https://www.coder.work/article/2033561
        log.debug(self.path)
        
        # .tlf is actually a zip file
        with ZipFile(self.path, "r") as z:
            # file 'flow' contain all detail 
            with z.open( 'flow' ) as f:  
                data = f.read()  
                data_json = json.loads(data.decode("utf-8"))
        
        return data_json
    

    def consistent_path(self, path):
        
        path = path.replace('/',"\\")
        
        return path
        
    
    def format_hyper(self, node, baseType, connection = 'None'):
        
        con_type = 'localfile'      
        if baseType == self.input_name:
            try:
                name = connection['connectionAttributes']['dbname'] # last update is in the connection
            except:
                name = node['connectionAttributes']['dbname']
         
        if baseType == self.output_name:          
            name = node['hyperOutputFile']
        
        # must with copy(), or the same items occur
        # ref: https://ithelp.ithome.com.tw/articles/10221255
        source_format = self.source_format.copy()
        source_format['baseType'] = baseType
        source_format['con_type'] = con_type
        source_format['name'] = self.consistent_path(name)
        
        return source_format 
 
    
    def format_csv(self, node, baseType, connection = 'None'):
        
        con_type = 'localfile'
        if baseType == self.input_name:
            try:
                name = connection['connectionAttributes']['filename']
            except:
                # for old version
                try:
                    name = node['connectionAttributes']['filename']
                except:
                    name = node['connectionAttributes']['directory']
         
        if baseType == self.output_name:          
            name = node['csvOutputFile']

        source_format = self.source_format.copy()
        source_format['baseType'] = baseType
        source_format['con_type'] = con_type
        source_format['name'] = self.consistent_path(name)
        
        return source_format      
    
    
    def format_excel(self, node, baseType, connection = 'None'):
        
        con_type = 'localfile'
        if baseType == self.input_name:
            name = connection['connectionAttributes']['filename']
        
        source_format = self.source_format.copy()
        source_format['baseType'] = baseType
        source_format['con_type'] = con_type
        source_format['name'] = self.consistent_path(name)
      
        return source_format


    def format_db(self, node, baseType, connection = 'None'):
        
        con_type = 'db'
        if baseType == self.input_name:
            server = connection['connectionAttributes']['server']
            # get dbname 
            dbname = connection['connectionAttributes']['dbname']
            if dbname == '':
                dbname = node['connectionAttributes']['dbname']
            # get table name
            try:
                table = node['relation']['table']
            except:
                # for custom sql query
                table = node['relation']['query']
        
        source_format = self.source_format.copy()
        source_format['baseType'] = baseType
        source_format['con_type'] = con_type
        source_format['server'] = server
        source_format['dbname'] = dbname
        source_format['table'] = table
   
        return source_format      


    def format_tableauserver(self, node, baseType, connection = 'None'):
        
        con_type =   'tableauserver'      
        if baseType == self.input_name:
            server = connection['connectionAttributes']['server'] + '/#/site/' + connection['connectionAttributes']['siteUrlName']
            project = node['connectionAttributes']['projectName']
            datasourceName = node['connectionAttributes']['datasourceName']
         
        if baseType == self.output_name:          
            server = node['serverUrl']
            project = node['projectName']
            datasourceName = node['datasourceName']

        source_format = self.source_format.copy()
        source_format['baseType'] = baseType
        source_format['con_type'] = con_type
        source_format['server'] = server
        source_format['project'] = project
        source_format['datasourceName'] = datasourceName        

        return source_format


    def list_sources(self):
                
        sources = []
        nodes = self.flow['nodes']
        connections = self.flow['connections']

        for node_id in list(nodes):
            log.debug(f"node_id: {node_id}")
            node = nodes[node_id]
            
            if node['baseType'] == 'input':
                baseType = self.input_name
                connection_id = node['connectionId']
                connection = connections[connection_id]
                log.debug(f"list_sources, input, node_id = {node}, connection_id = {connection_id}, connection = {connection}")
                # determine file_type
                try:
                    # hyper 
                    if connection['connectionAttributes']['class'] == 'hyper':
                        source_input = self.format_hyper(node, baseType, connection)
                    # csv
                    if 'LoadCsv' in node['nodeType']:
                        source_input = self.format_csv(node, baseType, connection)
                    # excel
                    if 'LoadExcel' in node['nodeType']:
                        source_input = self.format_excel(node, baseType, connection)               
                    # db
                    if (connection['connectionAttributes']['class'] == 'postgres' or 
                        connection['connectionAttributes']['class'] == 'snowflake'):
                        source_input = self.format_db(node, baseType, connection)
                    # tableauserver
                    if 'LoadSqlProxy' in node['nodeType']:
                        source_input = self.format_tableauserver(node, baseType, connection)
                        
                    sources.append(source_input)
                    
                except Exception:
                    print(f"some inputs cannot be decoded")
                    print(f"flow:{self.path}, node_id:{node_id}, baseType:{baseType}, nodetype:{node['nodeType']}")
                    raise
                    
            if node['baseType'] == 'output':
                baseType = self.output_name
                # determine file_type
                log.debug(f"list_sources, output, node_id = {node}, baseType = {baseType}")
                try:
                    # hyper 
                    if 'WriteToHyper' in node['nodeType']:
                        source_output = self.format_hyper(node, baseType)
                    # csv
                    if 'WriteToCsv' in node['nodeType']:
                        source_output = self.format_csv(node, baseType)
                    # tableauserver
                    if 'PublishExtract' in node['nodeType']:
                        source_output = self.format_tableauserver(node, baseType)  
                        
                    sources.append(source_output) 
                                              
                except Exception:
                    print(f"some outputs cannot be decoded")
                    print(f"flow:{self.path}, node_id:{node_id}, baseType:{baseType}, nodetype:{node['nodeType']}")
                    raise

        return sources