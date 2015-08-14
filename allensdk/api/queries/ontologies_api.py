# Copyright 2015 Allen Institute for Brain Science
# This file is part of Allen SDK.
#
# Allen SDK is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Allen SDK is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Allen SDK.  If not, see <http://www.gnu.org/licenses/>.

from allensdk.api.queries.rma_api import RmaApi
from allensdk.api.cache import Cache
import pandas as pd

class OntologiesApi(RmaApi, Cache):
    '''
    See: `Atlas Drawings and Ontologies <http://help.brain-map.org/display/api/Atlas+Drawings+and+Ontologies>`_
    '''
    
    def __init__(self, base_uri=None, cache=False):
        super(OntologiesApi, self).__init__(base_uri)
        Cache.__init__(self, cache=cache)
    
    
    def get_atlases_table(self, atlas_id=None, brief=True, fmt='json'):
        '''List Atlases available through the API
        with associated ontologies and structure graphs.
        
        Parameters
        ----------
        atlas_id : integer, optional
        brief : boolean, optional
            True (default) requests only name and id fields.
        fmt : string, optional
            json (default) or xml
        
        Returns
        -------
        url : string
            The constructed URL
        
        Notes
        -----
        This query is based on the
        `table of available Atlases <http://help.brain-map.org/display/api/Atlas+Drawings+and+Ontologies>`_.
        See also: `Class: Atlas <http://api.brain-map.org/doc/Atlas.html>`_
        '''
        associations = []
        
        if atlas_id != None:
            associations.append('[id$eq%d],' % (atlas_id))
        
        associations.extend(['structure_graph(ontology),',
                             'graphic_group_labels'])
        
        associations_string = ''.join(associations)
        
        if brief == True:
            only_fields = ['atlases.id',
                           'atlases.name',
                           'atlases.image_type',
                           'ontologies.id',
                           'ontologies.name',
                           'structure_graphs.id',
                           'structure_graphs.name',
                           'graphic_group_labels.id',
                           'graphic_group_labels.name']
            
            only_string = self.quote_string(','.join(only_fields))
        
            atlas_data = self.model_query('Atlas',
                                          include=[associations_string],
                                          criteria=[associations_string],
                                          only=[only_string])
        
        else:
            atlas_data = self.model_stage('Atlas',
                                          include=[associations_string],
                                          criteria=[associations_string])
        
        return atlas_data    
    
    
    def get_ontology(self, structure_graph_id):
        '''Retrieve.'''
        data = self.do_query(self.build_query,
                                   self.read_data)
        
        return data
    

    def cache_structures(self,
                         path,
                         *args,
                         **kwargs):
        if self.cache == True:
            # fetch all structures from graph_id = 1
            data = self.get_structures(*args, **kwargs)
            structures = pd.DataFrame(data)
            structures.set_index(['id'], inplace=True)                            
 
        all_structures = pd.DataFrame.from_csv(path)
                 
        return all_structures
    
    def get_structures(self,
                       structure_graph_ids=None,
                       structure_graph_names=None,                    
                       structure_set_ids=None,
                       structure_set_names=None,
                       order = ['structures.graph_order'],
                       num_rows='all',
                       count=False):
        criteria_list = []
        
        if structure_graph_ids != None:
            if type(structure_graph_ids) is not list:
                structure_graph_ids = [ structure_graph_ids ]
            criteria_list.append('[graph_id$in%s]' % ','.join(str(i) for i in structure_graph_ids))
        
        if structure_graph_names != None:
            if type(structure_graph_names) is not list:
                structure_graph_names = [ structure_graph_names ]
            structure_graph_names = [self.quote_string(n) for n in structure_graph_names]
            criteria_list.append('graph[structure_graphs.name$in%s]' % (','.join(structure_graph_names)))
        
        if structure_set_ids != None:
            if type(structure_set_ids) is not list:
                structure_set_ids = [ structure_set_ids ]
            criteria_list.append('[graph_id$in%s]' % ','.join(str(i) for i in structure_graph_ids))

        if structure_set_names != None:
            if type(structure_set_names) is not list:
                structure_set_names = [ structure_set_names ]
            structure_set_names = [self.quote_string(n) for n in structure_set_names]
            criteria_list.append('structure_sets[name$in%s]' % (','.join(structure_set_names)))
            
        criteria_string = ','.join(criteria_list)
        
        data = self.model_query('Structure',
                                criteria=criteria_string,
                                order=order,
                                num_rows=num_rows,
                                count=count)
        
        return data
    
    
    def unpack_structure_set_ancestors(self, structure_dataframe):
        ancestors = structure_dataframe['structure_id_path'].apply(
            lambda e: [int(a) for a in e.split('/')[1:-1]])
        structure_ancestors = [
            [n for n in ancestors_n] for ancestors_n in ancestors
        ]
        structure_dataframe['structure_set_ancestor'] = structure_ancestors