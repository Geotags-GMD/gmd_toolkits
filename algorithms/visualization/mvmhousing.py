"""
Model exported as python.
Name : 1. MVM-Housing Characteristics
Group : 
With QGIS : 32815
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsCoordinateReferenceSystem
import processing
import os

class MvmhousingCharacteristics(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('input_f2_csv', 'Input F2 CSV', types=[QgsProcessing.TypeVector], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('input_citymun_boundary', 'Input CityMun Boundary', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Hccitymunfloor', 'HC-CityMun-Floor', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Hccitymunroof', 'HC-CityMun-Roof', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Hccitymunwall', 'HC-CityMun-Wall', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(9, model_feedback)
        results = {}
        outputs = {}

        # Define paths to QML style files
        qml_base_path = os.path.join(os.path.dirname(__file__), 'style')  # Dynamically construct the path
        floor_style = os.path.join(qml_base_path, '1. HH_HC-Floor.qml')
        roof_style = os.path.join(qml_base_path, '2.HH_HC-Roof.qml')
        wall_style = os.path.join(qml_base_path, '3. HH_HC-Wall.qml')
        admbdry_style = os.path.join(qml_base_path, '4. CityMun_AdmBdry.qml')

        # Load layer into project (AdmBdry)
        alg_params = {
            'INPUT': parameters['input_citymun_boundary'],
            'NAME': 'CityMun_AdmBdry'
        }
        outputs['LoadLayerIntoProjectAdmbdry'] = processing.run('native:loadlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Create points layer from table
        alg_params = {
            'INPUT': parameters['input_f2_csv'],
            'MFIELD': '',
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
            'XFIELD': 'longitude',
            'YFIELD': 'latitude',
            'ZFIELD': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CreatePointsLayerFromTable'] = processing.run('native:createpointslayerfromtable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # HC-CityMun-Wall
        alg_params = {
            'FIELDS_MAPPING': [{'alias': '','comment': '','expression': '"unique_id"','length': 0,'name': 'unique_id','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'alias': '','comment': '','expression': '"uuid"','length': 0,'name': 'uuid','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'alias': '','comment': '','expression': '"case_id"','length': 0,'name': 'case_id','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'alias': '','comment': '','expression': '"latitude"','length': 0,'name': 'latitude','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'alias': '','comment': '','expression': '"longitude"','length': 0,'name': 'longitude','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'alias': '','comment': '','expression': '"wall"','length': 0,'name': 'wall','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'}],
            'INPUT': outputs['CreatePointsLayerFromTable']['OUTPUT'],
            'OUTPUT': parameters['Hccitymunwall']
        }
        outputs['Hccitymunwall'] = processing.run('native:refactorfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Hccitymunwall'] = outputs['Hccitymunwall']['OUTPUT']

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # AdmBdry
        alg_params = {
            'INPUT': outputs['LoadLayerIntoProjectAdmbdry']['OUTPUT'],
            'STYLE': admbdry_style
        }
        outputs['Admbdry'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # HC-CityMun-Roof
        alg_params = {
            'FIELDS_MAPPING': [{'alias': '','comment': '','expression': '"unique_id"','length': 0,'name': 'unique_id','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'alias': '','comment': '','expression': '"uuid"','length': 0,'name': 'uuid','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'alias': '','comment': '','expression': '"case_id"','length': 0,'name': 'case_id','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'alias': '','comment': '','expression': '"latitude"','length': 0,'name': 'latitude','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'alias': '','comment': '','expression': '"longitude"','length': 0,'name': 'longitude','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'alias': '','comment': '','expression': '"roof"','length': 0,'name': 'roof','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'}],
            'INPUT': outputs['CreatePointsLayerFromTable']['OUTPUT'],
            'OUTPUT': parameters['Hccitymunroof']
        }
        outputs['Hccitymunroof'] = processing.run('native:refactorfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Hccitymunroof'] = outputs['Hccitymunroof']['OUTPUT']

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Roof
        alg_params = {
            'INPUT': outputs['Hccitymunroof']['OUTPUT'],
            'STYLE': roof_style
        }
        outputs['Roof'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # HC-CityMun-Floor
        alg_params = {
            'FIELDS_MAPPING': [{'alias': '','comment': '','expression': '"unique_id"','length': 0,'name': 'unique_id','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'alias': '','comment': '','expression': '"uuid"','length': 0,'name': 'uuid','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'alias': '','comment': '','expression': '"case_id"','length': 0,'name': 'case_id','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'alias': '','comment': '','expression': '"latitude"','length': 0,'name': 'latitude','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'alias': '','comment': '','expression': '"longitude"','length': 0,'name': 'longitude','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'alias': '','comment': '','expression': '"floor"','length': 0,'name': 'floor','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'}],
            'INPUT': outputs['CreatePointsLayerFromTable']['OUTPUT'],
            'OUTPUT': parameters['Hccitymunfloor']
        }
        outputs['Hccitymunfloor'] = processing.run('native:refactorfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Hccitymunfloor'] = outputs['Hccitymunfloor']['OUTPUT']

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Wall
        alg_params = {
            'INPUT': outputs['Hccitymunwall']['OUTPUT'],
            'STYLE': wall_style
        }
        outputs['Wall'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Floor
        alg_params = {
            'INPUT': outputs['Hccitymunfloor']['OUTPUT'],
            'STYLE': floor_style
        }
        outputs['Floor'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        return '1. MVM-Housing Characteristics'

    def displayName(self):
        return '1. MVM-Housing Characteristics'

    def group(self):
        return 'Visualization'

    def groupId(self):
        return 'vis-group'

    def createInstance(self):
        return MvmhousingCharacteristics()
