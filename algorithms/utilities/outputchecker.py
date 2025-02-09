from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingException,
    QgsProcessingParameterFeatureSink,
    QgsFeatureSink,
    QgsApplication
)
from qgis.PyQt.QtCore import QVariant

class OutputChecker(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    COLUMN_NAME = 'COLUMN_NAME'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                'Input Point Layer',
                [QgsProcessing.TypeVectorPoint]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterField(
                self.COLUMN_NAME,
                'Column to check for null values',
                '',
                self.INPUT,
                QgsProcessingParameterField.Any
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                'Temporary Layer'
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        feedback.pushInfo("Starting Output Check algorithm...")

        source = self.parameterAsSource(parameters, self.INPUT, context)
        column_name = self.parameterAsString(parameters, self.COLUMN_NAME, context)

        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        column_index = source.fields().indexFromName(column_name)
        if column_index == -1:
            raise QgsProcessingException(f'No column named "{column_name}" found in the input layer')

        feedback.pushInfo(f'Checking for null values in column: {column_name}')

        has_value = False
        for feature in source.getFeatures():
            if feature[column_index]:
                has_value = True
                break

        if not has_value:
            feedback.pushInfo("No values found in the selected column. No layer will be created.")
            return {}

        feedback.pushInfo("Values found in the selected column. Creating temporary layer...")

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            source.fields(),
            source.wkbType(),
            source.sourceCrs()
        )

        if sink is None:
            raise QgsProcessingException("Sink creation failed.")

        for feature in source.getFeatures():
            sink.addFeature(feature, QgsFeatureSink.FastInsert)

        feedback.pushInfo("Temporary layer created successfully.")

        return {self.OUTPUT: dest_id}

    def name(self):
        return 'outputcheck'

    def displayName(self):
        return 'Output Check'
    
    def group(self):
        return 'Utilities'

    def groupId(self):
        return 'utilities_process'

    def createInstance(self):
        return OutputChecker()


