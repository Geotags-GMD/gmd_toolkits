"""
Model exported as python.
Name : 2. MVM-Households with PWD Members
Group : 
With QGIS : 32815
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsCoordinateReferenceSystem
import processing
import os

class MvmhouseholdsWithPwdMembers(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('input_f2_csv', 'Input F2 CSV', types=[QgsProcessing.TypeVector], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('input_citymun_boundary', 'Input CityMun Boundary', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(5, model_feedback)
        results = {}
        outputs = {}


         # Define paths to QML style files
        qml_base_path = os.path.join(os.path.dirname(__file__), 'style')  # Dynamically construct the path
        citymun_admbdry_style = os.path.join(qml_base_path, '4. CityMun_AdmBdry.qml')
        hh_with_pwd_style = os.path.join(qml_base_path, '5. HH_with_PWD.qml')

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

        # Load layer into project (PWD)
        alg_params = {
            'INPUT': outputs['CreatePointsLayerFromTable']['OUTPUT'],
            'NAME': 'CityMun_HH with PWD'
        }
        outputs['LoadLayerIntoProjectPwd'] = processing.run('native:loadlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # AdmBdry - Apply style
        alg_params = {
            'INPUT': outputs['LoadLayerIntoProjectAdmbdry']['OUTPUT'],
            'STYLE': citymun_admbdry_style
        }
        outputs['Admbdry'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # HH with PWD - Apply style
        alg_params = {
            'INPUT': outputs['LoadLayerIntoProjectPwd']['OUTPUT'],
            'STYLE': hh_with_pwd_style
        }
        outputs['HhWithPwd'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        return '2. MVM-Households with PWD Members'

    def displayName(self):
        return '2. MVM-Households with PWD Members'

    def group(self):
        return 'Visualization'

    def groupId(self):
        return 'vis-group'

    def createInstance(self):
        return MvmhouseholdsWithPwdMembers()