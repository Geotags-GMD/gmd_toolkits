"""
Model exported as python.
Name : 4. MVM-Proximity to Evacuation Centers
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

class MvmproximityToEvacuationCenters(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('input_sf_layer', 'Input SF Layer', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('input_f2_csv', 'Input F2 CSV', types=[QgsProcessing.TypeVector], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('input_citymun_boundary', 'Input CityMun Boundary', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Citymun_buffer_1km', 'CityMun_Buffer_1km', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Citymun_hh', 'CityMun_HH', type=QgsProcessing.TypeVectorPoint, createByDefault=True, defaultValue='TEMPORARY_OUTPUT'))
        self.addParameter(QgsProcessingParameterFeatureSink('Citymun_evacuation', 'CityMun_Evacuation', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Citymun_hhwithin', 'CityMun_HH-within', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))



    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(11, model_feedback)
        results = {}
        outputs = {}

         # Define paths to QML style files
        qml_base_path = os.path.join(os.path.dirname(__file__), 'style')
        citymun_admbdry_layer_style = os.path.join(qml_base_path, '4. CityMun_AdmBdry.qml')
        evacuation_center_layer_style = os.path.join(qml_base_path, '7. Evacuation Center.qml')
        buffered_evacuation_center_layer_style = os.path.join(qml_base_path, '8. Buffered_Evacuation Center.qml')
        hhfor_proximity_layer_style =  os.path.join(qml_base_path, '9. HH-for Proximity.qml')
        hh_withinfor_proximity_layer_style = os.path.join(qml_base_path, '10. HH_within-for Proximity.qml')

        # Load layer into project (AdmBdry)
        alg_params = {
            'INPUT': parameters['input_citymun_boundary'],
            'NAME': 'CityMun_AdmBdry'
        }
        outputs['LoadLayerIntoProjectAdmbdry'] = processing.run('native:loadlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Reproject layer (SF)
        alg_params = {
            'CONVERT_CURVED_GEOMETRIES': False,
            'INPUT': parameters['input_sf_layer'],
            'OPERATION': '',
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:32651'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ReprojectLayerSf'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Create points layer from table (F2)
        alg_params = {
            'INPUT': parameters['input_f2_csv'],
            'MFIELD': '',
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
            'XFIELD': 'longitude',
            'YFIELD': 'latitude',
            'ZFIELD': '',
            'OUTPUT': parameters['Citymun_hh']
        }
        outputs['CreatePointsLayerFromTableF2'] = processing.run('native:createpointslayerfromtable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Citymun_hh'] = outputs['CreatePointsLayerFromTableF2']['OUTPUT']

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # AdmBdry
        alg_params = {
            'INPUT': outputs['LoadLayerIntoProjectAdmbdry']['OUTPUT'],
            'STYLE': citymun_admbdry_layer_style
        }
        outputs['Admbdry'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # HH Style
        alg_params = {
            'INPUT': outputs['CreatePointsLayerFromTableF2']['OUTPUT'],
            'STYLE': hhfor_proximity_layer_style
        }
        outputs['HhStyle'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Extract by expression (Evac Center)
        alg_params = {
            'EXPRESSION': '"SPECTYPE" in ( \'0404_DESIGNATED EVACUATION CENTER (STANDALONE; DRRM, EMERGENCY SITES)\' , \'0404_DESIGNATED EVACUATION CENTER (STANDALONE; EMERGENCY SITES)\' ) or "subtype" in (\'0319_Evacuation Center\')',
            'INPUT': outputs['ReprojectLayerSf']['OUTPUT'],
            'OUTPUT': parameters['Citymun_evacuation']
        }
        outputs['ExtractByExpressionEvacCenter'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Citymun_evacuation'] = outputs['ExtractByExpressionEvacCenter']['OUTPUT']

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Buffer
        alg_params = {
            'DISSOLVE': True,
            'DISTANCE': 1000,
            'END_CAP_STYLE': 0,  # Round
            'INPUT': outputs['ExtractByExpressionEvacCenter']['OUTPUT'],
            'JOIN_STYLE': 0,  # Round
            'MITER_LIMIT': 2,
            'SEGMENTS': 100,
            'SEPARATE_DISJOINT': False,
            'OUTPUT': parameters['Citymun_buffer_1km']
        }
        outputs['Buffer'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Citymun_buffer_1km'] = outputs['Buffer']['OUTPUT']

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Extract by location (HH within)
        alg_params = {
            'INPUT': outputs['CreatePointsLayerFromTableF2']['OUTPUT'],
            'INTERSECT': outputs['Buffer']['OUTPUT'],
            'PREDICATE': [6],  # are within
            'OUTPUT': parameters['Citymun_hhwithin']
        }
        outputs['ExtractByLocationHhWithin'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Citymun_hhwithin'] = outputs['ExtractByLocationHhWithin']['OUTPUT']

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Evacuation Center Style
        alg_params = {
            'INPUT': outputs['ExtractByExpressionEvacCenter']['OUTPUT'],
            'STYLE': evacuation_center_layer_style
        }
        outputs['EvacuationCenterStyle'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Buffer Style
        alg_params = {
            'INPUT': outputs['Buffer']['OUTPUT'],
            'STYLE': buffered_evacuation_center_layer_style
        }
        outputs['BufferStyle'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # HH-within Style
        alg_params = {
            'INPUT': outputs['ExtractByLocationHhWithin']['OUTPUT'],
            'STYLE': hh_withinfor_proximity_layer_style
        }
        outputs['HhwithinStyle'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        return '4. MVM-Proximity to Evacuation Centers'

    def displayName(self):
        return '4. MVM-Proximity to Evacuation Centers'

    def group(self):
        return 'Visualization'

    def groupId(self):
        return 'vis-group'

    def createInstance(self):
        return MvmproximityToEvacuationCenters()